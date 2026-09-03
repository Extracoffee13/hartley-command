# B9 GSC Weekly Review — Claude QA Gate

**Run:** 2026-08-03 (week ending 2026-08-10)
**Reviewer:** Claude (QA gate over Hermes)
**Verdict:** PASS — nothing applied; no live-site changes made.

## Hermes review queue
- Status: `awaiting_claude_review`, generated 2026-08-03 06:00 (fresh).
- New issues: 0 · Resolved: 0 · Proposed fixes: 0 · Critical money-page risks: none.
- Deltas flat: indexed 266→266; not-indexed 791→791. No new 404 spike, no noindex change, no manual actions, no security issues.
- One "no action" note (confirmed correct): 270 "Excluded by noindex" URLs are Yoast-noindexed product_tag/archive pages; no money pages affected.

**Result:** No proposed fixes to approve/reject. Hermes was NOT instructed to apply anything (nothing to apply). No unreviewed change reached the live site.

## Mandatory independent checks (run every week regardless of queue)

### Redirect catch-all check on /product(-category) — PASS (no catch-all)
Plugin-config API check (`/wp-json/redirection/v1/redirect?filterBy[url]=product`) could NOT be completed: the browser session is not authenticated to wp-admin (endpoint returned a themed 404; footer shows logged-out state). Credentials were not entered.

Verified functionally instead by probing live redirect behavior:
- `/product-category/monument-signs/` → 200, self-canonical, `index,follow`, full category grid renders. No redirect.
- `/product-category/property-branding/` → 301 → `/portfolio/`.
- Because sibling categories render while only one redirects, there is **no regex catch-all** on the `/product-category` tree (a catch-all would redirect all of them).
- **No URL observed redirects to `/services-brand-9/`.** The hard-block failure mode is absent.

### Money-page gallery spot-check — PASS
- `/product-category/property-branding/` does NOT redirect to `/services-brand-9/`; it 301s to `/portfolio/`, which fully renders every category gallery (wp-content/uploads imagery) and links to every `/product/` page. No galleries hidden.
- `/product/monument-signs/` → 200, `index,follow`, ~50-image gallery intact.
- `/product/home-builder-exterior-signs/` → 200, self-canonical, healthy.

## For Bobby's awareness (not blocking)
1. **`/product-category/property-branding/` 301s to `/portfolio/`** while sibling category archives (e.g. monument-signs) render in place. Not harmful (portfolio preserves the imagery; no catch-all), but the inconsistency is worth a glance — confirm this single redirect is intentional vs. leftover.
2. **Plugin-config redirect audit couldn't run unauthenticated.** Functional probing covers the catastrophic case, but to run the exact `/wp-json/redirection/v1/redirect` audit each week, the scheduled Chrome session needs a logged-in wp-admin cookie for brand9signs.com.
