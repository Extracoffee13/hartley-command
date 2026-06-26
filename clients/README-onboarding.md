# PRAGMA Mirror — client onboarding

The Mirror engine (`hermes-sandbox/calls/pragma-mirror/`) is multi-tenant. One
codebase serves every client; each client is just a folder + a config file.

## Add a new client (free Reports tier)

1. Copy the template:
   `cp -r clients/_template clients/<slug>` (slug = short id, e.g. `tlc`)
2. Edit `clients/<slug>/config.json` — set name, domain, category, phone, email,
   competitors, service_areas, geotarget_communities, key_pages, aeo_queries,
   llm_questions. Set `"tier": "free"`, `"mode": "recommend"`.
3. Run the scan:
   `python3 run.py --client <slug>`
   → writes `clients/<slug>/brand-insights/latest.json` + `recommendations.json`.
   Free tier = measure + diagnose + queued recommendations. No site writes.

## Upgrade a client to paid (Auto-fix tier)

1. In the client's WordPress, create an Application Password (Users → Profile →
   Application Passwords). Store it in `~/.hermes/.env`:
   `<SLUG>_WP_USER=...` and `<SLUG>_WP_APP_PASSWORD=...`
2. In `config.json` set `wp.user_env` / `wp.app_password_env` to those names,
   `"tier": "paid"`, `"mode": "auto-remediate"`.
3. Run the auto-fix engine:
   `python3 auto_apply.py --client <slug> --apply --max 3`
   → creates the missing local/community pages via WP REST. Additive-only,
   dup-guarded, rate-limited, change-logged (`autofix-log.json`), WP-revision undo.

## Daily cycle

`run_daily.sh` runs scan → auto-fix for the primary client (b9). For additional
clients, add `python3 run.py --client <slug> && python3 auto_apply.py --client <slug> --apply --max 3`
lines, or schedule per-client.

## Notes / current limits

- The **scanner is fully client-agnostic** (config-driven) — free Reports work
  for any client today.
- The **auto-fix page templates** in `auto_apply.py` (`build_local_page`) are
  written for a **local-service / signage vertical**. For a different vertical,
  add a per-vertical content template (the structure — answer-first + FAQPage +
  LocalBusiness schema — stays the same; only the body copy changes).
- The live V4 dashboard currently renders one primary client (b9). A
  multi-client selector reads `clients/<slug>/brand-insights/latest.json`.
