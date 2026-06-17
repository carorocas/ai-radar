---
name: ai-radar-news-signals
description: Convert recent artificial intelligence news into structured AI Radar signals. Use when the user asks for latest/recent AI news, AI Radar signals, daily AI news JSON snapshots, or saving AI news using the AI Radar contract.
---

# AI Radar News Signals

## Workflow

1. Inspect the current repository before writing files.
2. If the user asks for latest or recent news, consult Notion first for the `AI Radar Sources` page.
3. Read active sources from Notion and generate/update `codex/config/sources.json` as the local cache.
4. If Notion does not respond, use `codex/config/sources.json`.
5. If both Notion and the cache are unavailable, use the fallback sources in this skill and report the fallback clearly.
6. Group active sources by `tipo` and assign each group to its own subagent when the user asks for multiple agents or parallel source work:
   - `fuente_oficial`
   - `repo_tecnico`
   - `comunidad`
   - `medio_secundario`
7. If the user asks for latest or recent news, browse the web using only the active sources for each group. Prioritize primary or reputable sources such as AP News, Reuters, official company blogs, TechCrunch, The Verge, MIT Technology Review, or government/regulator pages when no configured source exists for a group.
8. Select 5 signals by relevance, not by search order. Prefer a balanced mix across product launches, models, infrastructure, regulation, safety, funding, developer tools, and adoption.
9. Normalize each item into an AI Radar signal:

```json
{
  "id": "stable-kebab-case-id",
  "title": "short signal title",
  "source": {
    "name": "source name",
    "url": "https://example.com/article",
    "published_at": "YYYY-MM-DD or source-provided date"
  },
  "evidence": "what happened, grounded in the source",
  "impact": "why it matters for builders or AI Radar",
  "action": "what to monitor, test, compare, or avoid next",
  "status": "vigilar"
}
```

10. Use these statuses unless the repository already defines others:
   - `vigilar`
   - `probar_pronto`
   - `esperar_para_probar`
   - `vigilar_infraestructura`
   - `riesgo_alto`

11. If the user asks to save the search and no contract exists, create `contracts/ai-radar-daily-signals.schema.json`.
12. Save the daily snapshot as `data/daily/YYYY-MM-DD-ai-signals.json`.
13. When the user asks to save, persist, store, archive, or register signals, use `guardar-senales-airradar` after writing the snapshot.
14. Validate created JSON files with the local shell JSON parser available in the environment.
15. Report what files were created or updated, what source path was used, whether SQLite persistence ran, and what validation was run.

## Source Loading

Always try sources in this order:

1. Notion page `AI Radar Sources`.
2. Local cache `codex/config/sources.json`.
3. Built-in fallback sources from this skill.

When Notion works, write the cache with this shape:

```json
{
  "contract_version": "ai-radar-sources/v1",
  "generated_at": "ISO-8601 timestamp",
  "source": "notion",
  "notion_page": "AI Radar Sources",
  "groups": {
    "fuente_oficial": [
      {
        "name": "OpenAI News",
        "url": "https://openai.com/news/",
        "status": "activa",
        "usage": "Comunicados oficiales, lanzamientos de modelos, politicas y anuncios institucionales."
      }
    ]
  }
}
```

Only use sources with `status` equal to `activa`.

## Subagent Grouping

When using subagents, create one independent task per source group:

| Group | Subagent focus |
|---|---|
| `fuente_oficial` | Official announcements, labs, companies, regulators, governments |
| `repo_tecnico` | GitHub repos, releases, technical changelogs, open source AI projects |
| `comunidad` | Hacker News, Reddit, Hugging Face community, Product Hunt, public forums |
| `medio_secundario` | AP, Reuters, TechCrunch, The Verge, MIT Technology Review, Bloomberg, FT |

Each subagent must return candidates with title, source, URL, date, evidence, impact, action, and status. The parent agent deduplicates, verifies suspicious claims, and consolidates the final AI Radar signals.

## Persistence Handoff

Use the `guardar-senales-airradar` skill when the user asks to save results. The handoff should run:

```powershell
python codex\scripts\validate_contracts.py codex\data\daily\YYYY-MM-DD-ai-signals.json
python codex\scripts\save_signals.py --input codex\data\daily\YYYY-MM-DD-ai-signals.json --source-mode notion --pretty
```

Set `--source-mode` according to the source loader result:

- `notion` when Notion sources were loaded and cached.
- `cache` when `codex/config/sources.json` was used because Notion failed.
- `fallback --fallback-used` when built-in fallback sources were used.

## Fallback Sources

Use these only if Notion and `codex/config/sources.json` are unavailable:

```json
{
  "fuente_oficial": [
    {
      "name": "OpenAI News",
      "url": "https://openai.com/news/"
    }
  ],
  "repo_tecnico": [
    {
      "name": "GitHub Trending AI",
      "url": "https://github.com/trending?spoken_language_code=&since=daily"
    }
  ],
  "comunidad": [
    {
      "name": "Hacker News",
      "url": "https://news.ycombinator.com/"
    }
  ],
  "medio_secundario": [
    {
      "name": "AP News Artificial Intelligence",
      "url": "https://apnews.com/hub/artificial-intelligence"
    }
  ]
}
```

If fallback is used, include a short note in the final answer:

`Fallback usado: Notion no respondio; se uso codex/config/sources.json.`

or:

`Fallback usado: Notion y cache local no estaban disponibles; se usaron fuentes por defecto de la skill.`

## Contract

Use this daily snapshot shape unless an existing repo contract says otherwise:

```json
{
  "contract_version": "ai-radar-daily-signals/v1",
  "date": "YYYY-MM-DD",
  "query": "user request or normalized search query",
  "generated_at": "ISO-8601 timestamp",
  "signals": []
}
```

The schema must require:

- `contract_version`
- `date`
- `query`
- `signals`

Each signal must require:

- `id`
- `title`
- `source`
- `evidence`
- `impact`
- `action`
- `status`

## Evidence Rules

- Include direct URLs for every source.
- Do not invent dates, commands, services, repositories, or integrations.
- If a source date is unavailable, write the clearest source-provided relative date or `unknown`, and say so in the final response.
- Keep evidence concise and attributable.
- Distinguish facts from inference when assessing impact or action.

## Safety And Cost

- Do not use paid APIs, paid browsing, external model services, deployments, or third-party installations for this workflow.
- Web browsing is appropriate only when the user asks for recent/latest news or explicitly asks to search.
- Prefer local files and local validation for saving snapshots.
