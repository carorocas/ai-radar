#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path


ALLOWED_STATUSES = {
    "vigilar",
    "probar_pronto",
    "esperar_para_probar",
    "vigilar_infraestructura",
    "riesgo_alto",
}


def utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def repo_root():
    return Path(__file__).resolve().parents[1]


def default_db_path():
    configured = os.environ.get("AIRADAR_DB_PATH")
    if configured:
        return Path(configured)
    return repo_root() / "data" / "airadar.sqlite"


def stable_run_id(payload):
    basis = "|".join(
        [
            payload.get("date", ""),
            payload.get("query", ""),
            str(payload.get("generated_at", "")),
        ]
    )
    return hashlib.sha256(basis.encode("utf-8")).hexdigest()[:16]


def source_id(source):
    url = source.get("url", "").strip()
    name = source.get("name", "").strip()
    basis = url or name
    return hashlib.sha256(basis.encode("utf-8")).hexdigest()[:16]


def require_string(obj, key, context):
    value = obj.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{context}: falta string requerido '{key}'")
    return value


def validate_signal(signal, index):
    context = f"signals[{index}]"
    require_string(signal, "id", context)
    require_string(signal, "title", context)
    require_string(signal, "evidence", context)
    require_string(signal, "impact", context)
    require_string(signal, "action", context)
    status = require_string(signal, "status", context)
    if status not in ALLOWED_STATUSES:
        raise ValueError(f"{context}: status no permitido '{status}'")

    source = signal.get("source")
    if not isinstance(source, dict):
        raise ValueError(f"{context}: falta objeto 'source'")
    require_string(source, "name", f"{context}.source")
    require_string(source, "url", f"{context}.source")
    require_string(source, "published_at", f"{context}.source")


def load_snapshot(path):
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    require_string(payload, "contract_version", "snapshot")
    require_string(payload, "date", "snapshot")
    require_string(payload, "query", "snapshot")
    signals = payload.get("signals")
    if not isinstance(signals, list) or not signals:
        raise ValueError("snapshot: 'signals' debe ser un arreglo no vacio")

    seen_ids = set()
    for index, signal in enumerate(signals):
        validate_signal(signal, index)
        signal_id = signal["id"]
        if signal_id in seen_ids:
            raise ValueError(f"snapshot: id duplicado '{signal_id}'")
        seen_ids.add(signal_id)

    return payload


def connect(db_path):
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_schema(conn):
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS sources (
          id TEXT PRIMARY KEY,
          type TEXT,
          name TEXT NOT NULL,
          url TEXT NOT NULL UNIQUE,
          status TEXT NOT NULL DEFAULT 'activa',
          usage TEXT,
          created_at TEXT NOT NULL,
          updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS signals (
          id TEXT PRIMARY KEY,
          title TEXT NOT NULL,
          source_id TEXT NOT NULL,
          source_url TEXT NOT NULL,
          published_at TEXT NOT NULL,
          evidence TEXT NOT NULL,
          impact TEXT NOT NULL,
          action TEXT NOT NULL,
          status TEXT NOT NULL,
          importance_score INTEGER,
          score_confidence TEXT,
          raw_json TEXT NOT NULL,
          created_at TEXT NOT NULL,
          updated_at TEXT NOT NULL,
          FOREIGN KEY (source_id) REFERENCES sources(id)
        );

        CREATE TABLE IF NOT EXISTS runs (
          id TEXT PRIMARY KEY,
          query TEXT NOT NULL,
          date TEXT NOT NULL,
          snapshot_path TEXT NOT NULL,
          source_mode TEXT NOT NULL,
          fallback_used INTEGER NOT NULL DEFAULT 0,
          created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS run_signals (
          run_id TEXT NOT NULL,
          signal_id TEXT NOT NULL,
          position INTEGER NOT NULL,
          PRIMARY KEY (run_id, signal_id),
          FOREIGN KEY (run_id) REFERENCES runs(id),
          FOREIGN KEY (signal_id) REFERENCES signals(id)
        );

        CREATE TABLE IF NOT EXISTS validations (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          target_type TEXT NOT NULL,
          target_id TEXT NOT NULL,
          result TEXT NOT NULL,
          notes TEXT,
          created_at TEXT NOT NULL
        );
        """
    )


def upsert_source(conn, source, now):
    sid = source_id(source)
    conn.execute(
        """
        INSERT INTO sources (id, type, name, url, status, usage, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(url) DO UPDATE SET
          name = excluded.name,
          updated_at = excluded.updated_at
        """,
        (
            sid,
            source.get("type"),
            source["name"],
            source["url"],
            source.get("status", "activa"),
            source.get("usage"),
            now,
            now,
        ),
    )
    row = conn.execute("SELECT id FROM sources WHERE url = ?", (source["url"],)).fetchone()
    return row["id"]


def upsert_signal(conn, signal, sid, now):
    source = signal["source"]
    conn.execute(
        """
        INSERT INTO signals (
          id, title, source_id, source_url, published_at, evidence, impact, action,
          status, importance_score, score_confidence, raw_json, created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
          title = excluded.title,
          source_id = excluded.source_id,
          source_url = excluded.source_url,
          published_at = excluded.published_at,
          evidence = excluded.evidence,
          impact = excluded.impact,
          action = excluded.action,
          status = excluded.status,
          importance_score = excluded.importance_score,
          score_confidence = excluded.score_confidence,
          raw_json = excluded.raw_json,
          updated_at = excluded.updated_at
        """,
        (
            signal["id"],
            signal["title"],
            sid,
            source["url"],
            source["published_at"],
            signal["evidence"],
            signal["impact"],
            signal["action"],
            signal["status"],
            signal.get("importance_score"),
            signal.get("score_confidence"),
            json.dumps(signal, ensure_ascii=True, sort_keys=True),
            now,
            now,
        ),
    )


def save_snapshot(conn, payload, snapshot_path, source_mode, fallback_used):
    now = utc_now()
    run_id = payload.get("run_id") or stable_run_id(payload)

    conn.execute(
        """
        INSERT INTO runs (id, query, date, snapshot_path, source_mode, fallback_used, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
          query = excluded.query,
          date = excluded.date,
          snapshot_path = excluded.snapshot_path,
          source_mode = excluded.source_mode,
          fallback_used = excluded.fallback_used
        """,
        (
            run_id,
            payload["query"],
            payload["date"],
            str(snapshot_path),
            source_mode,
            1 if fallback_used else 0,
            now,
        ),
    )

    inserted = 0
    for position, signal in enumerate(payload["signals"], start=1):
        sid = upsert_source(conn, signal["source"], now)
        upsert_signal(conn, signal, sid, now)
        conn.execute(
            """
            INSERT INTO run_signals (run_id, signal_id, position)
            VALUES (?, ?, ?)
            ON CONFLICT(run_id, signal_id) DO UPDATE SET position = excluded.position
            """,
            (run_id, signal["id"], position),
        )
        inserted += 1

    conn.execute(
        """
        INSERT INTO validations (target_type, target_id, result, notes, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            "run",
            run_id,
            "ok",
            f"Saved {inserted} signals from {snapshot_path.name}",
            now,
        ),
    )
    return run_id, inserted


def parse_args():
    parser = argparse.ArgumentParser(
        description="Guarda un snapshot diario de AI Radar en SQLite local."
    )
    parser.add_argument("--input", required=True, type=Path, help="JSON diario de AI Radar.")
    parser.add_argument("--db", type=Path, default=default_db_path(), help="Ruta SQLite.")
    parser.add_argument(
        "--source-mode",
        default="json_snapshot",
        help="Origen de fuentes usado en la corrida: notion, cache, fallback o json_snapshot.",
    )
    parser.add_argument(
        "--fallback-used",
        action="store_true",
        help="Marca que la corrida uso fallback de fuentes.",
    )
    parser.add_argument("--pretty", action="store_true", help="Imprime JSON indentado.")
    return parser.parse_args()


def main():
    args = parse_args()
    try:
        payload = load_snapshot(args.input)
        with connect(args.db) as conn:
            init_schema(conn)
            run_id, saved = save_snapshot(
                conn,
                payload,
                args.input.resolve(),
                args.source_mode,
                args.fallback_used,
            )
    except (OSError, sqlite3.Error, ValueError, json.JSONDecodeError) as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=True), file=sys.stderr)
        raise SystemExit(1)

    result = {
        "contract_version": "ai-radar-save-result/v1",
        "db_path": str(args.db),
        "run_id": run_id,
        "saved_signals": saved,
        "source_mode": args.source_mode,
        "fallback_used": bool(args.fallback_used),
    }
    print(json.dumps(result, ensure_ascii=True, indent=2 if args.pretty else None))


if __name__ == "__main__":
    main()
