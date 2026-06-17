#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path


ALLOWED_STATUSES = {
    "vigilar",
    "probar_pronto",
    "esperar_para_probar",
    "vigilar_infraestructura",
    "riesgo_alto",
}


def require_string(obj, key, context, errors):
    value = obj.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{context}: falta string requerido '{key}'")


def validate_daily(path):
    errors = []
    try:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, json.JSONDecodeError) as error:
        return [f"{path}: {error}"]

    require_string(payload, "contract_version", "snapshot", errors)
    require_string(payload, "date", "snapshot", errors)
    require_string(payload, "query", "snapshot", errors)
    signals = payload.get("signals")
    if not isinstance(signals, list) or not signals:
        errors.append("snapshot: 'signals' debe ser un arreglo no vacio")
        return errors

    seen_ids = set()
    seen_urls = set()
    for index, signal in enumerate(signals):
        context = f"signals[{index}]"
        for key in ["id", "title", "evidence", "impact", "action", "status"]:
            require_string(signal, key, context, errors)
        signal_id = signal.get("id")
        if signal_id in seen_ids:
            errors.append(f"{context}: id duplicado '{signal_id}'")
        seen_ids.add(signal_id)
        if signal.get("status") not in ALLOWED_STATUSES:
            errors.append(f"{context}: status no permitido '{signal.get('status')}'")

        source = signal.get("source")
        if not isinstance(source, dict):
            errors.append(f"{context}: falta objeto 'source'")
            continue
        for key in ["name", "url", "published_at"]:
            require_string(source, key, f"{context}.source", errors)
        url = source.get("url")
        if url in seen_urls:
            errors.append(f"{context}: source.url duplicada '{url}'")
        seen_urls.add(url)

    return errors


def parse_args():
    parser = argparse.ArgumentParser(description="Valida snapshots JSON de AI Radar.")
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="Archivos JSON. Si se omite, valida codex/data/daily/*.json.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    paths = args.paths
    if not paths:
        root = Path(__file__).resolve().parents[1]
        paths = sorted((root / "data" / "daily").glob("*.json"))

    results = []
    has_errors = False
    for path in paths:
        errors = validate_daily(path)
        if errors:
            has_errors = True
            results.append({"file": str(path), "result": "error", "errors": errors})
        else:
            results.append({"file": str(path), "result": "ok", "errors": []})

    print(json.dumps({"results": results}, ensure_ascii=True, indent=2))
    if has_errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
