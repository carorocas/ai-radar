---
name: guardar-senales-airradar
description: Use when the user asks to save, persist, store, sync, register, or archive AI Radar signals, daily AI news snapshots, JSON signal files, or search results into local storage, SQLite, or the AI Radar persistence layer.
---

# Guardar Senales AI Radar

## Workflow

1. Inspect the repo and locate the JSON snapshot to save.
2. Validate snapshots before saving:

```powershell
python codex\scripts\validate_contracts.py codex\data\daily\YYYY-MM-DD-ai-signals.json
```

3. Persist valid snapshots into local SQLite:

```powershell
python codex\scripts\save_signals.py --input codex\data\daily\YYYY-MM-DD-ai-signals.json --source-mode notion --pretty
```

4. Report:
   - snapshot path;
   - SQLite path;
   - run id;
   - number of saved signals;
   - source mode: `notion`, `cache`, `fallback`, or `json_snapshot`;
   - validation result.

## Storage Policy

- Use JSON snapshots as evidence.
- Use SQLite as the local operational store.
- Use Notion only to configure source lists, not as the primary signal database.
- Do not use Supabase, paid APIs, cloud databases, deployments, or third-party installs unless the user says IT approved them.

## Environment

Supported optional variables:

```powershell
AIRADAR_DB_PATH=codex\data\airadar.sqlite
AIRADAR_STORAGE=sqlite
AIRADAR_SOURCES_CACHE=codex\config\sources.json
AIRADAR_NOTION_SOURCES_PAGE="AI Radar Sources"
```

If variables are missing, use local defaults.

## Validation Rules

Before saving, ensure:

- daily JSON parses;
- `signals` is a non-empty array;
- each signal has `id`, `title`, `source`, `evidence`, `impact`, `action`, and `status`;
- `source` has `name`, `url`, and `published_at`;
- signal IDs are unique;
- source URLs are not duplicated inside the same snapshot;
- status is one of the allowed AI Radar statuses.

## Fallback Reporting

If the snapshot was created without Notion sources, pass the right mode:

- `--source-mode cache` when `codex/config/sources.json` was used.
- `--source-mode fallback --fallback-used` when built-in fallback sources were used.
- `--source-mode json_snapshot` when the source path is unknown.
