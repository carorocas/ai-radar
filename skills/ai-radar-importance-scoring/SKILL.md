---
name: ai-radar-importance-scoring
description: Use when AI Radar needs to score, rank, compare, or save artificial intelligence news signals by importance, source authority, author reputation, audience traffic, reach, visits, popularity, or evidence strength.
---

# AI Radar Importance Scoring

## Overview

Score each AI Radar news signal from 0 to 100 using three factors:

- source importance: 40 points
- author reputation: 30 points
- traffic or audience reach: 30 points

Prefer measured evidence. If traffic or author data is unavailable without paid tools, use transparent heuristics and lower `score_confidence`.

## Workflow

1. Inspect the repo contract before changing files.
2. For each signal, collect or infer:
   - source name and URL;
   - author name, if present;
   - traffic/reach evidence, if public and free;
   - notes explaining the score.
3. Do not use paid APIs, paid traffic databases, scraping behind login, or external model services.
4. Run `scripts/score_signal.py` for deterministic scoring when signal metadata is available.
5. Add scoring fields to each signal:

```json
{
  "importance_score": 82,
  "score_confidence": "medium",
  "score_breakdown": {
    "source_importance": 36,
    "author_reputation": 22,
    "traffic_reach": 24
  },
  "score_notes": [
    "AP News is a high-authority wire source.",
    "Author reputation was inferred from byline presence only.",
    "Traffic was estimated from outlet-level reach, not article analytics."
  ]
}
```

## Scoring Rules

### Source Importance, 0-40

- 36-40: primary source or top-tier wire/global outlet, e.g. official company/regulator blog, AP, Reuters.
- 28-35: respected technology/business outlet with editorial standards, e.g. TechCrunch, The Verge, MIT Technology Review, Bloomberg, Financial Times.
- 18-27: niche but credible outlet, specialist blog, university lab, analyst publication.
- 8-17: aggregator, repost, lightly edited secondary coverage.
- 0-7: unknown, unverifiable, social-only, or low-context source.

### Author Reputation, 0-30

- 26-30: named reporter/researcher with recognized beat expertise or primary institutional author.
- 18-25: named author with relevant publication history, but not clearly field-leading.
- 10-17: named author with limited visible reputation or unclear specialization.
- 5-9: staff/editorial byline with no named author.
- 0-4: anonymous, unverifiable, or missing author.

### Traffic Or Reach, 0-30

- 26-30: major global outlet/platform, official post from a large AI lab, regulator, or hyperscaler; likely very high reach.
- 18-25: large technology/business outlet or widely cited specialist source.
- 10-17: niche outlet with credible but limited audience.
- 4-9: small site, repost, or unknown audience.
- 0-3: no audience evidence and low discoverability.

Use article-level traffic only when available from free public evidence. Otherwise score outlet-level reach and state that in `score_notes`.

## Confidence

- `high`: source, author, and traffic/reach are supported by direct or strong public evidence.
- `medium`: source is clear, but author or traffic is inferred.
- `low`: two or more factors are inferred or unknown.

## Output Contract

If an AI Radar contract exists, extend it minimally rather than replacing it. Add optional fields:

- `importance_score`: integer 0-100
- `score_confidence`: `high`, `medium`, or `low`
- `score_breakdown.source_importance`: integer 0-40
- `score_breakdown.author_reputation`: integer 0-30
- `score_breakdown.traffic_reach`: integer 0-30
- `score_notes`: array of strings

## Common Mistakes

- Do not claim exact traffic unless the source provides exact article analytics.
- Do not treat social virality as traffic unless there is direct evidence.
- Do not over-score anonymous articles from major outlets; source and author are separate factors.
- Do not hide uncertainty. Use `score_confidence` and notes.
