# B9 GSC Weekly Review — Claude QA Gate

**Run:** 2026-08-17 (week ending 2026-08-24)
**Reviewer:** Claude (QA gate over Hermes)
**Verdict:** PASS on the queue — nothing applied, no live-site changes made.
**Flag:** One structural change since last week needs Bobby's call (see §4).

---

## 1. Hermes review queue

- `gsc-weekly-review.json` — status `awaiting_claude_review`, generated 2026-08-17 10:00Z (fresh, <1 day).
- New issues: **0** · Resolved: **0** · Proposed fixes: **0** · Critical money-page risks: **none**.
- Deltas flat: indexed 266→266; not-indexed 791→791.
- Top not-indexed reasons unchanged: Crawled–currently not indexed 373 · Excluded by noindex 270 · Not found (404) 98.
- No manual actions, no security issues.
- One "no action" note, confirmed correct: the 270 noindexed URLs are Yoast-noindexed product_tag/archive pages; no money pages affected.

**Result:** nothing to approve or reject. Hermes was **not** dispatched — with zero approved fixes there is nothing to apply. No unreviewed change reached the live site.

---

## 2. Money-page health sweep — PASS

All returned 200, self-canonical, **no noindex**, galleries intact:

| URL | Status | Canonical | Robots | Images |
|---|---|---|---|---|
| `/` | 200 | self | none | 57 |
| `/services-brand-9/` | 200 | self | none | 27 |
| `/contact/` | 200 | self | none | 27 |
| `/product/monument-signs/` | 200 | self | none | 55 |
| `/product/home-builder-exterior-signs/` | 200 | self | none | 180 |
| `/portfolio/` | 200 | self | none | 203 |

`/product/*` pages are **not** redirected — they resolve natively. That was the primary catastrophic-failure vector and it is clean.

---

## 3. Hard-block check on `/product(-category)` — condition PRESENT, not the July failure mode

**The prescribed check could not be run as written.** `/wp-json/` returns **404 sitewide** — the WordPress REST API is gone and the Redirection plugin endpoint (`/wp-json/redirection/v1/redirect?filterBy[url]=product`) does not exist. B9 is now the static DreamHost build; any redirect is server-level (.htaccess), not plugin-managed. The runbook step needs updating.

**Verified functionally instead. Every `/product-category/*` URL probed now 301s to `/portfolio/`:**

| Requested | Final | Redirected | Bytes |
|---|---|---|---|
| `/product-category/property-branding/` | `/portfolio/` | yes | 109,302 |
| `/product-category/monument-signs/` | `/portfolio/` | yes | 109,302 |
| `/product-category/wayfinding/` | `/portfolio/` | yes | 109,302 |
| `/product-category/` | `/portfolio/` | yes | 109,302 |

Identical byte length on every one = a **catch-all across the `/product-category` tree**.

**This is a change from last week.** The 2026-08-03 QA recorded `/product-category/monument-signs/` returning 200 and rendering its grid in place, with only `property-branding` redirecting — which is why that run concluded "no catch-all." The catch-all appeared between 2026-08-03 and 2026-08-17.

**But the July failure mode is absent, and the damage it caused is not occurring:**

- Destination is `/portfolio/`, **not** `/services-brand-9/`.
- `/portfolio/` is a genuine gallery hub, not a thin page: 203 real `wp-content/uploads` photos, 25 category sections (incl. "Property Branding — 10 sections"), 185 links out to `/product/*` pages.
- Photos are **not** hidden. Screenshot-verified: category browser renders, 24 categories / 100+ product lines.
- `/product/*` remains natively reachable.

---

## 4. Needs Bobby's decision — I did NOT delete the catch-all

The hard rule says auto-delete any `/product(-category)` catch-all. **I deliberately did not**, because deleting it here looks likely to cause the harm the rule exists to prevent:

1. The static build appears to have **no `/product-category/*` pages left** — `/portfolio/` emits **zero** `/product-category` links; categories are now accordion sections on `/portfolio/`. Removing the redirect would 404 all ~24 category URLs on top of the 98 404s already in GSC.
2. The deletion mechanism in the runbook (Redirection plugin) **no longer exists** — WP REST is decommissioned.
3. The evidence reads as a deliberate portfolio re-architecture, not the July regression: the destination preserves the imagery and the product tree.
4. Per the standing rule — *if a proposed fix is at all doubtful, reject it and flag it for Bobby* — an irreversible live-site change that isn't clearly correct doesn't get made.

**Question for Bobby:** was the `/product-category/*` → `/portfolio/` consolidation intentional?

- **If yes** — no action, but the runbook's hard block should be rewritten to allow this specific destination, otherwise a future run will "fix" it and break the site.
- **If no** — this needs a rebuild of per-category pages, not a redirect deletion (deleting alone yields 404s).

**Residual SEO cost either way:** ~24 distinct category archive URLs now collapse to one page, so per-category search intent ("property branding signs," "wayfinding signs") has no distinct landing page. If those categories carry query volume, per-category pages under `/portfolio/{category}/` would recover it.

**Not confirmed:** whether the redirect is 301 or 302 — the intermediate response wasn't readable from the browser context. If it's a 302, it should be a 301.

---

## 5. Minor — data hygiene

`brand-insights/latest.json` is internally inconsistent: `visibility_score.composite` = **43** (flat 43 for all 7 trend days), but the `interpretation` string reads "composite brand visibility **48**/100." One of the two is stale. Worth fixing so the dashboard doesn't report a number the data doesn't support.

---

## Summary

- Issues found by Hermes this week: **0**
- Fixes approved & applied: **0** (none proposed; Hermes not dispatched)
- Fixes rejected: **0** (none proposed)
- Independent findings: **1 flagged** — new `/product-category/*` catch-all → `/portfolio/`, non-destructive, not deleted, awaiting Bobby's intent call
- Live-site changes made this run: **none**
