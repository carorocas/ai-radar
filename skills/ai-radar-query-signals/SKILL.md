---
name: ai-radar-query-signals
description: Use when the user asks to consult, list, retrieve, filter, order, rank, or show saved AI Radar signals from daily JSON snapshots by day, count, amount, limit, order, importance, newest, oldest, or title.
---

# AI Radar Query Signals

## Workflow

1. Inspect the AI Radar workspace before answering.
2. Use `codex/scripts/query_saved_signals.py` when the user asks to consult persisted signals from SQLite.
3. Use `codex/scripts/query_daily_signals.py` when the user specifically asks to consult a JSON snapshot.
4. Ask for clarification only if the requested day, count, or order is ambiguous and no reasonable default exists.
5. Use these defaults:
   - day: current local date if the user says "hoy"; otherwise use the requested date.
   - limit: 5 when the user does not specify a number.
   - order: `newest` for SQLite, `original` for JSON snapshots.
6. Return the tool output or summarize it, depending on what the user asked.

## Tool

Run from the workspace root or from `codex/`:

```powershell
python codex\scripts\query_saved_signals.py --day 2026-06-10 --limit 3 --order importance_desc --pretty
```

For JSON snapshot evidence:

```powershell
python codex\scripts\query_daily_signals.py --day 2026-06-10 --limit 3 --order importance_desc --pretty
```

Supported `--order` values:

- `original`
- `newest`
- `oldest`
- `importance_desc`
- `importance_asc`
- `title_asc`
- `title_desc`

## Output

The tool returns JSON:

```json
{
  "contract_version": "ai-radar-query-signals/v1",
  "date": "YYYY-MM-DD",
  "source_file": "path/to/daily-json",
  "order": "importance_desc",
  "limit": 3,
  "total_signals": 5,
  "returned_signals": 3,
  "signals": []
}
```

## Notes

- Do not invent signals if the daily JSON does not exist.
- If the user asks for importance ordering but the signals do not have `importance_score`, the tool keeps unscored signals at the bottom for descending order.
- Do not use paid APIs or external services for this query workflow.
