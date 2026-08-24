# B9 GSC Weekly Review — Claude QA Gate

**Run:** 2026-08-24 (week ending 2026-08-31)
**Reviewer:** Claude (QA gate over Hermes)
**Verdict:** PASS on the queue — nothing proposed, nothing applied, no live-site changes made.
**Open item:** the `/product-category/*` → `/portfolio/` catch-all flagged on 2026-08-17 is still live and still awaiting Bobby's intent call.

---

## 1. Hermes review queue

- `gsc-weekly-review.json` — status `awaiting_claude_review`, generated 2026-08-24 10:00Z (fresh, <1 day). No stale-queue escalation needed.
- New issues: **0** · Resolved: **0** · Proposed fixes: **0** · Critical money-page risks: **none**.
- Deltas flat, identical to last week: indexed 266→266; not-indexed 791→791.
- Top not-indexed reasons unchanged: Crawled–currently not indexed 373 · Excluded by noindex 270 · Not found (404) 98.
- No manual actions, no security issues.
- One "no action" note, re-confirmed correct: the 270 noindexed URLs are Yoast-noindexed product_tag/archive pages; no money pages affected.

**Result:** nothing to approve or reject. **Hermes was not dispatched** — with zero approved fixes there is nothing to apply. No unreviewed change reached the live site.

---

## 2. Money-page health sweep — PASS

All 200, self-canonical, **no noindex**, no redirect, galleries intact:

| URL | Status | Redirect | Canonical | Robots | Upload images |
|---|---|---|---|---|---|
| `/` | 200 | none | self | none | 31 |
| `/services-brand-9/` | 200 | none | self | none | 24 |
| `/contact/` | 200 | none | self | none | 24 |
| `/portfolio/` | 200 | none | self | none | 198 |
| `/product/monument-signs/` | 200 | none | self | none | 52 |
| `/product/home-builder-exterior-signs/` | 200 | none | self | none | 173 |
| `/product/builder-barricades/` | 200 | none | self | none | 16 |
| `/product/state-park-signs/` | 200 | none | self | none | 2 |

`/product/*` resolves natively — the primary catastrophic-failure vector is clean.

---

## 3. Hard-block check on `/product(-category)` — condition unchanged from last week

**Prescribed check still cannot be run as written.** `/wp-json/` and `/wp-json/redirection/v1/redirect` both return **410 Gone** (last week: 404). The WordPress REST API is deliberately decommissioned; B9 is the static DreamHost build. There is no Redirection plugin to query or delete from. **The runbook step needs rewriting.**

**Verified functionally instead.** Every `/product-category/*` URL probed still redirects to `/portfolio/`:

| Requested | Final | Bytes |
|---|---|---|
| `/product-category/property-branding/` | `/portfolio/` | 109,340 |
| `/product-category/monument-signs/` | `/portfolio/` | 109,340 |
| `/product-category/wayfinding/` | `/portfolio/` | 109,340 |
| `/product-category/` | `/portfolio/` | 109,340 |

Identical byte length across all four = catch-all across the tree. Confirmed **HTTP-level** (a `redirect:"manual"` fetch returns `opaqueredirect`, which only occurs on a real 3xx) — not a JS redirect. Exact 3xx code still not readable from the browser context; unchanged from last week.

**The July failure mode remains absent:**

- Destination is `/portfolio/`, **not** `/services-brand-9/`.
- Photos are **not** hidden. Screenshot-verified this run: the category browser renders with 24 categories / 100+ product lines and live thumbnails (Banners, Builder Signage, Corporate Branding, Monument Signs, Hospitality Signage, etc.). 198 real `wp-content/uploads` photos on the page.
- `/product/*` remains natively reachable — 185 outbound `/product/` links from `/portfolio/`.

**I again did NOT delete the catch-all.** Same reasoning as 2026-08-17, plus one new piece of evidence:

1. `/portfolio/` emits **zero** `/product-category/` links — the static build has no category pages left. Deleting the redirect would 404 ~24 URLs on top of the 98 already in GSC.
2. **New this week:** `/sitemap.xml` (330 URLs) contains **zero** `/product-category/` entries and 92 `/product/` entries. The sitemap was regenerated to match the consolidation. That reads as deliberate re-architecture, not regression.
3. The prescribed deletion mechanism does not exist (WP REST 410).
4. Standing rule: if a fix is at all doubtful, reject and flag rather than apply. An irreversible live-site change that isn't clearly correct doesn't get made.

---

## 4. Additional checks run this week — all clean except §5

- **Sitemap coherence:** `/sitemap.xml` 200, 330 `<loc>` entries. Sampled 14 across the file — every one returned **200 with no redirect**. No stale or redirecting URLs being advertised to Google. `/sitemap_index.xml` 404s, but `/sitemap.xml` is the live canonical one, so this is cosmetic — worth confirming GSC has `/sitemap.xml` submitted, not the index path.
- **404 handling:** a bogus URL returns a true **404** (no soft-404, no redirect-to-home).
- **robots.txt:** 200, healthy. `Allow: /` sitewide; disallows `/wp-admin/`, `/wp-json/`, plugins, `/api/`, `/health`, `/session/`. All AI crawlers explicitly allowed (GPTBot, OAI-SearchBot, ChatGPT-User, ClaudeBot, Claude-Web, Claude-SearchBot, PerplexityBot, Perplexity-User, Google-Extended, Applebot, Amazonbot). Correct for the AEO strategy.

---

## 5. Needs Bobby's decision

### 5a. `/product-category/*` → `/portfolio/` consolidation — carried over, second week

Was this intentional?

- **If yes** — no action, but **the runbook's hard block must be rewritten** to whitelist `/portfolio/` as a permitted destination. As written, a future run is instructed to auto-delete this redirect, which would 404 ~24 category URLs.
- **If no** — the fix is rebuilding per-category pages, *not* deleting the redirect. Deleting alone yields 404s.

Residual SEO cost either way: ~24 category archive URLs collapse to one page, so per-category intent ("property branding signs," "wayfinding signs") has no distinct landing page. If those carry volume, per-category pages under `/portfolio/{category}/` would recover it.

### 5b. NEW — `/wp-login.php` is live and functional on a decommissioned WordPress

`/wp-admin/` → **410**. `/wp-json/` → **410**. But `/wp-login.php` → **200**, serving a real WordPress login form (`Log In ‹ Brand 9 Signs — WordPress`, 8,173 bytes).

Two problems:

1. **Attack surface.** A reachable WP login on a site whose WordPress is otherwise retired is a standing credential-stuffing / brute-force target with no operational benefit if nobody logs in anymore.
2. **robots.txt does not disallow it** — `/wp-admin/` and `/wp-json/` are disallowed, `/wp-login.php` is not.

I did **not** change this — blocking or removing it could lock out legitimate admin access, and that's your call, not mine. Recommended if you no longer use the WP backend: 410 it alongside `/wp-admin/`, or IP-restrict it.

---

## 6. Data hygiene — one item resolved, worth confirming

Last week `brand-insights/latest.json` was internally inconsistent (composite 43 vs. interpretation string saying 48). It now reads **composite 49 / interpretation "49/100"** — consistent. The 7-day trend `[48,48,48,48,48,54,49]` shows a one-day spike to 54 then settle at 49; worth a glance to confirm the 54 was a real measurement and not a probe artifact.

Site-health snapshot (GSC, May 21 – Aug 20): 266 clicks, 72,700 impressions, 0.4% CTR, avg position 30.6. Delta vs. prior: **clicks +15**, impressions −1,900, CTR +0.1pp, position +0.3.

---

## Summary

- Issues found by Hermes this week: **0**
- Fixes approved & applied: **0** (none proposed; Hermes not dispatched)
- Fixes rejected: **0** (none proposed)
- Independent findings: **2 flagged** — (a) `/product-category/*` catch-all, carried over, not deleted, awaiting intent call; (b) **new** — live `/wp-login.php` on a retired WordPress
- Live-site changes made this run: **none**
