# B9 GSC Weekly Review — Claude QA Gate
**Week ending 2026-09-07 · Reviewed 2026-08-31 · Queue generated 2026-08-31T10:00Z**

## Verdict: CLEAN WEEK — nothing dispatched to Hermes

Hermes proposed **0 fixes**. Nothing was approved, nothing was rejected, nothing was
applied to the live site. Hermes was **not** dispatched this run (no approved items = no
work order; dispatching an empty list would be pointless and adds risk).

---

## 1. Queue state (`gsc-weekly-review.json`)

| Metric | Before | After | Δ |
|---|---|---|---|
| Indexed | 266 | 266 | 0 |
| Not indexed | 791 | 791 | 0 |
| Crawled – currently not indexed | 373 | 373 | 0 |
| Excluded by 'noindex' | 270 | 270 | 0 |
| Not found (404) | 98 | 98 | 0 |
| Manual actions | none | none | — |
| Security issues | none | none | — |

New issues: 0 · Resolved: 0 · Proposed fixes: 0 · Money-page risks flagged: none.

The 270 `noindex` exclusions are Yoast-noindexed product_tag/archive URLs — expected, no
action. Concur.

---

## 2. HARD BLOCK check — /product & /product-category catch-all redirects

Run independently, as required, not taken from Hermes' word.

**The specified check could not run as written, and here is why:** the WordPress backend
is fully retired. `wp-admin` and the entire `wp-json` namespace — including
`/wp-json/redirection/v1/redirect` — now return **410 Gone**. There is no Redirection
plugin left to query or delete rules from. The site is the static HTML build on
SiteGround/DreamHost (per `b9-website-architecture`).

So I verified the *outcome* the rule exists to protect instead — the galleries — by
direct live probe:

- `/product-category/property-branding/` → **301 → `/portfolio/`** (HTTP 200)
- `/product-category/01-marketing-branding/` → **301 → `/portfolio/`**
- `/product-category/16-environmental-graphic-design/` → **301 → `/portfolio/`**
- **No redirect anywhere to `/services-brand-9/`.** The July regression is not present.
- `/portfolio/` renders **26 category accordions, 176 product links, 92 unique product
  pages, 205 images**.
- **All 100 unique image sources return HTTP 200** (95 of them legacy `wp-content/uploads/`
  paths — all serving fine, no 410s).
- **All 92 product money pages resolve 200 directly**, zero redirected, zero swallowed.
- Money pages spot-checked 200 and un-redirected: `/`, `/portfolio/`, `/contact/`,
  `/case-studies/`, `/services-brand-9/`, `/product/development-signage/`,
  `/product/home-builder-exterior-signs/`, `/sitemap.xml`.

**Ruling: the `/product-category/*` → `/portfolio/` catch-all is NOT deleted.**

The letter of the hard block says delete any catch-all on `/product-category`. I did not,
and this is the one judgment call in this run, so it is stated plainly:

1. The rule's stated harm — "silently hides thousands of product photos" — **does not
   occur here.** `/portfolio/` *is* the galleries; every photo and every product page is
   reachable and returns 200. That was verified on pixels and on status codes, not assumed.
2. The old `/product-category/` archive pages **no longer exist as files** in the static
   build. Deleting the redirect would 404 the entire legacy tree — that would *cause* the
   outage the rule is meant to prevent, not stop one.
3. `/portfolio/` is the documented, intended architectural successor to the
   `/product-category/` tree per `b9-website-architecture`.

Deleting would have been the irreversible, destructive move on a money-page tree. Per the
hard rule ("if at all doubtful, reject and flag rather than apply"), I flagged it.
**→ Needs Bobby's decision: item A below.**

---

## 3. Site health (`brand-insights/site-health.json`, crawl 2026-08-31T11:38Z)

Health score **70/100**. Crawl: 249 pages, **all HTTP 200**, avg load 0.72s, zero pages
over 2s, **zero broken links**. Structurally the site is in good shape.

The entire 30-point deduction is two on-page hygiene issues, both unaddressed by Hermes:

- **180 pages with `<title>` over 60 chars** (−15). Worst offenders run 90–126 chars, so
  they truncate in SERPs. Includes money pages, e.g.
  `/product/premium-graphic-design-services/` (95),
  `/which-companies-install-community-monument-signs-in-master-planned-communities/` (95).
- **66 meta descriptions over 155 chars** (−15).

Hermes proposed nothing for either. **→ Needs Bobby's decision: item B below.**

---

## 4. Visibility mirror (`brand-insights/latest.json`, 11:00Z)

Composite AIVI **54/100 (YELLOW)**, live pulse 50. 31 open recommendations, 25 high
priority. Sentiment unmeasured. Autofix engine last ran 2026-07-07 (10 local landing pages,
verified live). No regression signal this week.

---

## 5. Approved / applied

None. Nothing proposed, nothing approved, nothing touched the live site.

## 6. Rejected

None proposed to reject. The one item declined was a *standing instruction*, not a Hermes
proposal — the catch-all deletion, reasoned above.

---

## Needs Bobby's decision

**A. The hard-block rule is now aimed at a system that no longer exists.** It tells this
review to query the Redirection plugin and delete catch-alls, but WordPress is 410'd and
the redirect that exists is correct and load-bearing. As written, following it literally
would break the legacy `/product-category/` tree. Recommend rewriting the rule to:
*"AUTO-REJECT any redirect on `/product` or `/product-category` that resolves anywhere
other than `/portfolio/` — verify by confirming `/portfolio/` renders its category
accordions and that every linked `/product/` page returns 200."* That preserves the real
intent and survives the static rebuild. **Do you want me to make that edit to the task
file?**

**B. Title/meta length cleanup — 180 + 66 pages, the whole 30-point health deduction.**
This is the single biggest available score movement and it is mechanical, reversible, and
low-risk (metadata only, no URL or content changes). It is also the kind of bulk edit
Hermes gets wrong. Recommend I generate the rewrites, you approve the list, and Hermes
applies via the proven batch-edit-over-SSH pattern. **Want me to prepare that list next
run?**

**C. Minor.** The `/portfolio/` hero reads "24 CATEGORIES" but the page now renders 26.
One-line copy fix, whenever something else is being deployed.

---

*QA gate: no unreviewed change reached the live site this week. All live claims above were
verified by direct authenticated-browser probe on 2026-08-31, not from Hermes' report or
from `curl` (which the sgcaptcha shield makes unreliable).*
