#!/usr/bin/env python3
import argparse
import json
import os
import sqlite3
import sys
from datetime import date
from pathlib import Path


ORDER_SQL = {
    "newest": "published_at DESC, title ASC",
    "oldest": "published_at ASC, title ASC",
    "importance_desc": "COALESCE(importance_score, -1) DESC, published_at DESC",
    "importance_asc": "COALESCE(importance_score, -1) ASC, published_at DESC",
    "title_asc": "title ASC",
    "title_desc": "title DESC",
}


def repo_root():
    return Path(__file__).resolve().parents[1]


def default_db_path():
    configured = os.environ.get("AIRADAR_DB_PATH")
    if configured:
        return Path(configured)
    return repo_root() / "data" / "airadar.sqlite"


def parse_args():
    parser = argparse.ArgumentParser(description="Consulta senales persistidas en SQLite.")
    parser.add_argument("--day", default=date.today().isoformat(), help="Dia YYYY-MM-DD.")
    parser.add_argument("--limit", "-n", type=int, default=5, help="Cantidad de senales.")
    parser.add_argument(
        "--order",
        choices=sorted(ORDER_SQL),
        default="newest",
        help="Orden de salida.",
    )
    parser.add_argument("--db", type=Path, default=default_db_path(), help="Ruta SQLite.")
    parser.add_argument("--pretty", action="store_true", help="Imprime JSON indentado.")
    return parser.parse_args()


def query_signals(db_path, day, limit, order):
    if not db_path.exists():
        raise FileNotFoundError(f"No existe SQLite: {db_path}")

    sql = f"""
        SELECT
          signals.id,
          signals.title,
          sources.name AS source_name,
          signals.source_url,
          signals.published_at,
          signals.evidence,
          signals.impact,
          signals.action,
          signals.status,
          signals.importance_score,
          signals.score_confidence
        FROM signals
        JOIN sources ON sources.id = signals.source_id
        WHERE signals.id IN (
          SELECT signal_id
          FROM run_signals
          JOIN runs ON runs.id = run_signals.run_id
          WHERE runs.date = ?
        )
        ORDER BY {ORDER_SQL[order]}
        LIMIT ?
    """

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(sql, (day, limit)).fetchall()

    signals = []
    for row in rows:
        signals.append(
            {
                "id": row["id"],
                "title": row["title"],
                "source": {
                    "name": row["source_name"],
                    "url": row["source_url"],
                    "published_at": row["published_at"],
                },
                "evidence": row["evidence"],
                "impact": row["impact"],
                "action": row["action"],
                "status": row["status"],
                "importance_score": row["importance_score"],
                "score_confidence": row["score_confidence"],
            }
        )
    return signals


def main():
    args = parse_args()
    if args.limit < 1:
        raise SystemExit("--limit debe ser mayor o igual a 1.")

    try:
        signals = query_signals(args.db, args.day, args.limit, args.order)
    except (OSError, sqlite3.Error) as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=True), file=sys.stderr)
        raise SystemExit(1)

    result = {
        "contract_version": "ai-radar-sqlite-query/v1",
        "date": args.day,
        "db_path": str(args.db),
        "order": args.order,
        "limit": args.limit,
        "returned_signals": len(signals),
        "signals": signals,
    }
    print(json.dumps(result, ensure_ascii=True, indent=2 if args.pretty else None))


if __name__ == "__main__":
    main()
