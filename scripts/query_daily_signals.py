#!/usr/bin/env python3
import argparse
import json
import sys
from datetime import date
from pathlib import Path


SUPPORTED_ORDERS = {
    "original",
    "newest",
    "oldest",
    "importance_desc",
    "importance_asc",
    "title_asc",
    "title_desc",
}


def load_snapshot(data_dir, day):
    path = data_dir / "daily" / f"{day}-ai-signals.json"
    if not path.exists():
        raise FileNotFoundError(f"No existe el JSON diario: {path}")

    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    signals = payload.get("signals")
    if not isinstance(signals, list):
        raise ValueError("El JSON diario debe tener un arreglo 'signals'.")

    return path, payload


def source_date(signal):
    source = signal.get("source")
    if not isinstance(source, dict):
        return ""
    return str(source.get("published_at", ""))


def importance_score(signal):
    score = signal.get("importance_score")
    if isinstance(score, (int, float)):
        return score
    return -1


def sorted_signals(signals, order):
    if order == "original":
        return list(signals)
    if order == "newest":
        return sorted(signals, key=source_date, reverse=True)
    if order == "oldest":
        return sorted(signals, key=source_date)
    if order == "importance_desc":
        return sorted(signals, key=importance_score, reverse=True)
    if order == "importance_asc":
        return sorted(signals, key=importance_score)
    if order == "title_asc":
        return sorted(signals, key=lambda signal: str(signal.get("title", "")).lower())
    if order == "title_desc":
        return sorted(
            signals,
            key=lambda signal: str(signal.get("title", "")).lower(),
            reverse=True,
        )
    raise ValueError(f"Orden no soportado: {order}")


def build_result(payload, source_path, day, limit, order):
    signals = sorted_signals(payload["signals"], order)
    selected = signals[:limit]
    return {
        "contract_version": "ai-radar-query-signals/v1",
        "date": day,
        "source_file": str(source_path),
        "order": order,
        "limit": limit,
        "total_signals": len(signals),
        "returned_signals": len(selected),
        "signals": selected,
    }


def parse_args():
    parser = argparse.ArgumentParser(
        description="Consulta N senales desde un JSON diario de AI Radar."
    )
    parser.add_argument(
        "--day",
        default=date.today().isoformat(),
        help="Dia a consultar en formato YYYY-MM-DD. Por defecto usa la fecha local actual.",
    )
    parser.add_argument(
        "--limit",
        "-n",
        type=int,
        default=5,
        help="Cantidad maxima de senales a devolver.",
    )
    parser.add_argument(
        "--order",
        default="original",
        choices=sorted(SUPPORTED_ORDERS),
        help="Orden de salida.",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data",
        help="Directorio base de datos de AI Radar. Por defecto usa codex/data.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Imprime JSON indentado.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    if args.limit < 1:
        raise SystemExit("--limit debe ser mayor o igual a 1.")

    try:
        source_path, payload = load_snapshot(args.data_dir, args.day)
        result = build_result(payload, source_path, args.day, args.limit, args.order)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=True), file=sys.stderr)
        raise SystemExit(1)

    indent = 2 if args.pretty else None
    print(json.dumps(result, ensure_ascii=True, indent=indent))


if __name__ == "__main__":
    main()
