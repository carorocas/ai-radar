#!/usr/bin/env python3
import argparse
import json
import sys


SOURCE_TIERS = {
    "official": 40,
    "ap news": 38,
    "associated press": 38,
    "reuters": 38,
    "techcrunch": 32,
    "the verge": 31,
    "mit technology review": 34,
    "bloomberg": 35,
    "financial times": 35,
    "the times": 30,
    "the guardian": 29,
    "investopedia": 24,
    "tom's hardware": 24,
}

REACH_TIERS = {
    "official": 28,
    "ap news": 28,
    "associated press": 28,
    "reuters": 28,
    "techcrunch": 23,
    "the verge": 23,
    "mit technology review": 22,
    "bloomberg": 25,
    "financial times": 25,
    "the times": 22,
    "the guardian": 23,
    "investopedia": 18,
    "tom's hardware": 17,
}


def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def normalized_name(name):
    return (name or "").strip().lower()


def score_source(source_name, is_primary=False):
    if is_primary:
        return 40
    return SOURCE_TIERS.get(normalized_name(source_name), 18)


def score_author(author_name, author_reputation=None, institutional_author=False):
    if author_reputation is not None:
        return clamp(int(author_reputation), 0, 30)
    if institutional_author:
        return 26
    if author_name and author_name.strip().lower() not in {"staff", "editorial", "unknown"}:
        return 18
    if author_name and author_name.strip().lower() in {"staff", "editorial"}:
        return 8
    return 4


def score_reach(source_name, traffic_reach=None, is_primary=False):
    if traffic_reach is not None:
        return clamp(int(traffic_reach), 0, 30)
    if is_primary:
        return 28
    return REACH_TIERS.get(normalized_name(source_name), 10)


def confidence(author_name, traffic_reach, author_reputation, source_known):
    inferred = 0
    if not source_known:
        inferred += 1
    if not author_name and author_reputation is None:
        inferred += 1
    if traffic_reach is None:
        inferred += 1
    if inferred == 0:
        return "high"
    if inferred <= 2:
        return "medium"
    return "low"


def build_notes(source_name, author_name, traffic_reach, author_reputation, is_primary):
    notes = []
    if is_primary:
        notes.append("Source was treated as primary evidence.")
    elif normalized_name(source_name) in SOURCE_TIERS:
        notes.append(f"{source_name} matched a known source tier.")
    else:
        notes.append("Source was not in the known tier table; default credible-source score was used.")

    if author_reputation is not None:
        notes.append("Author reputation score was provided explicitly.")
    elif author_name:
        notes.append("Author reputation was inferred from byline presence.")
    else:
        notes.append("Author reputation is low because no byline was provided.")

    if traffic_reach is not None:
        notes.append("Traffic/reach score was provided explicitly from available evidence.")
    else:
        notes.append("Traffic/reach was estimated from outlet-level reach, not exact article analytics.")
    return notes


def score_signal(signal):
    source = signal.get("source", {})
    source_name = source.get("name", "")
    is_primary = bool(signal.get("is_primary_source", False))
    author_name = signal.get("author")
    author_reputation = signal.get("author_reputation_score")
    traffic_reach = signal.get("traffic_reach_score")

    source_points = score_source(source_name, is_primary)
    author_points = score_author(author_name, author_reputation, institutional_author=is_primary)
    reach_points = score_reach(source_name, traffic_reach, is_primary)
    total = source_points + author_points + reach_points
    source_known = is_primary or normalized_name(source_name) in SOURCE_TIERS

    updated = dict(signal)
    updated["importance_score"] = total
    updated["score_confidence"] = confidence(author_name, traffic_reach, author_reputation, source_known)
    updated["score_breakdown"] = {
        "source_importance": source_points,
        "author_reputation": author_points,
        "traffic_reach": reach_points,
    }
    updated["score_notes"] = build_notes(
        source_name,
        author_name,
        traffic_reach,
        author_reputation,
        is_primary,
    )
    return updated


def main():
    parser = argparse.ArgumentParser(description="Score AI Radar signals by importance.")
    parser.add_argument("input", help="JSON file with either one signal or a daily snapshot with signals[]")
    parser.add_argument("--output", help="Output JSON file. Defaults to stdout.")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as handle:
        payload = json.load(handle)

    if isinstance(payload, dict) and isinstance(payload.get("signals"), list):
        payload = dict(payload)
        payload["signals"] = [score_signal(signal) for signal in payload["signals"]]
    elif isinstance(payload, dict):
        payload = score_signal(payload)
    else:
        raise SystemExit("Input must be a JSON object or an AI Radar daily snapshot.")

    text = json.dumps(payload, ensure_ascii=True, indent=2) + "\n"
    if args.output:
        with open(args.output, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()
