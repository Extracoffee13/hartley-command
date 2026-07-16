# Brand 9 Signs — AAIR Lift Tracker

**Frozen ruler:** 16-engine roster, 6 prompts, `POST https://prag-ma.ai/aair-checker.php` (~31s/scan).
**Tracked query (B9's real market):** business = "Brand 9 Signs", city = "Jacksonville, FL", service = "homebuilder signage".
**Rule:** never change the ruler between runs — only B9's real presence changes. Rescanned automatically every Friday.

| Date | AAIR /100 | Mirror (LLM) /100 | SLM /100 | Fraction | Notes |
|------|-----------|-------------------|----------|----------|-------|
| 2026-07-13 | 1 | 2 | 0 | 1/96 | Real-market baseline (homebuilder signage / Jacksonville). Only Perplexity names B9 (1/6). Week-1 optimization not yet started. |

---

## Intervention log — what changed between runs
*The ruler never changes; only B9's presence does. Every scan delta must be attributable to a dated, verified intervention below, or it is not a real result.*

**Principle locked 2026-07-15:** Every denominator is counted from scored results at write time. Never derive fractions from the panel dimensions.
**Principle locked 2026-07-16:** Never score a citation audit — or anything else — on an unverified fetch. A zero from a blocked or JS-shell response is a **no-read, not an absence**. Same rule as the scanner, applied to ourselves.

*Entries are newest-first.*

---

### 2026-07-16 (Thu) — Citation layer audited + corrected. **Bing Places claimed — the ChatGPT-search pipe is open.**

**Bing Places — claimed via GBP import. Highest-value action of the sprint to date.**
Imported from Google Business Profile → **instant verification**, no postcard. **Weekly Google→Bing sync enabled.** Record: `1970 Solomon St · (904) 272-3395 · brand9signs.com`. Publishing ETA 7–12 days → lands **2026-07-23 to 07-28**, at or just before Day-14.
- **Why it matters:** ChatGPT-search grounds on Bing. Before today Bing served **Yellowpages' 4.6/5 from 9 reviews**; GBP is **4.8/5 from 57**. The AI answer surface was reading a stale directory instead of the record we own. The pipe is now **GBP → (weekly sync) → Bing → ChatGPT-search** — every review gathered from here compounds into the answer layer automatically.
- **Bing fields are NOT editable:** *"To change these details, please update your information in Google and sync again."* **GBP is therefore the single control point.** This is direct evidence FOR the A-grade levers (reviews, GBP completeness) and against the rest — see `PRAGMA_Client_Lever_Playbook_v1.md`.
- **Open / not chasing:** Bing maps the category to **"Retail"**, not "Sign shop". **GBP is verified correct** (primary category *Sign shop*), so this is **Bing's taxonomy coarsely mapping our correct data** — not fixable from Google.

**Citation audit — verified through a rendering browser.**

| Source | State | Note |
|---|---|---|
| brand9signs.com | ✅ clean | 888 killed at source 7/15 (WPCode 9071) |
| GBP | ✅ clean | 4.8 · 57 · Sign shop · 1970 Solomon |
| Yelp | ✅ clean | **Claimed**, 1970 Solomon, (904) |
| Nextdoor | ✅ clean | 1970 Solomon |
| Houzz | ✅ clean | 1970 Solomon |
| Bing | ✅ fixed today | synced from GBP |
| **Chamber** | ✅ **correction SENT 7/16** | *"Your Message Has Been Sent."* Requested NAP fix **+ merge of the duplicate record** (28 reviews on the wrong listing, 26 on the right one). Awaiting their action. |
| **Wheree** | 🔴 dirty | `981 Kingsley` **and** `1950 Miller St Suite 3` |

**⚑ CORRECTION to the 7/15 entry — the pollution was over-counted.** It was logged that several sources published `985 Kingsley`. **Only the Chamber did.** The Yelp "985 Kingsley / 888" seen on Google's page one was **Google's stale cache of the Yelp page** — Yelp itself is claimed and correct. Logged because an inflated problem count is a measurement error and this tracker is the audit trail.

**⚑ But the aggregator theory HARDENED.** Three *distinct* wrong addresses are live — `985 Kingsley` (Chamber), `981 Kingsley` and `1950 Miller St Suite 3` (Wheree) — **none of which B9 has ever published.** `981` vs `985` is a one-digit corruption of the same record. Sites copying each other propagate *one* wrong address; **different vintages of the same upstream aggregator record, decaying independently, produce exactly this spread.** The upstream source is still unidentified and is **the only item here that regenerates after correction.**

**Method note (worth more than the corrections).** The first pass of this audit used `curl` and reported every source clean — because Chamber/Wheree/Yelp are JS-rendered or block non-browser agents, so all checks returned zero. **A zero from a failed fetch is a no-read, not an absence** — the identical defect Hermes fixed in the scanner the same day, reproduced in our own verification. Caught only by noticing that "1970 Solomon" also returned zero on a page known to contain it. Re-run through a rendering browser; principle locked above.

---

### 2026-07-15 (Wed) — RULER INTEGRITY: no-reads excluded from the denominator. **The Day-0 headline does not change.**

**The defect.** The two instruments were using **opposite denominator rules**:

| | numerator | denominator | errors |
|---|---|---|---|
| **Day-0 frozen ruler** (`b9-day0-2026-07-14.json`) | `named_cells` 5 | `total_cells` **256** | **counted inside the denominator** because 256 = 16 engines × 16 prompts; the denominator was the grid dimensions, not the result of counting cells. Day-0 had 6 no-reads (gemma4b ×4 HTTP 429, qwen72b ×2 "no choices") that were effectively treated as absences. |
| **Daily rescore** (`slm-mirror.json`) | `slm_total_cited` 10 | `slm_total_checks` **41** | **excluded** (48 attempted − 7 errored on 2026-07-14) |

Same business, same models, opposite arithmetic.

**The deeper finding.** The Day-0 denominators were **never error-aware because they were never counted**: 256 = 16×16, 160 = 10×16, 96 = 6×16. They were derived from the panel dimensions, not from results. The `per_engine[*].total` field is exactly 16 for every engine regardless of no-reads, and `per_prompt_named` arrays are length 16. The `errors` list is the same 6 cells duplicated as a convenience list; `detailed_matrix.error` matches them exactly by `engine + prompt_index`. This is a schema defect, not a transient-error problem.

**Why it threatens the sprint.** Error counts are rate limits — they are *not stable run to run*. Day-0 had 6; a later run could have 12. With errors inside the denominator, the score moves for reasons that have nothing to do with B9's presence. That is a **ruler artifact**, and this tracker's founding rule is that every delta must be attributable to a dated, verified intervention or it is not a real result.

**The decision (in force from 2026-07-15).** An unrecoverable cell is a **NO-READ, not an absence**. It is excluded from the denominator, reported separately, and never counted as `entity_found=false`. Every scan emits `attempted`, `scored`, `no_read`, `cited`, and `score = cited / scored`. **A score is never computed against `attempted`.** Cells are retried with exponential backoff — up to 3 attempts at ~2s / 4s / 8s — before being declared no-read, because most 429s are transient.

**The baseline survives — verified arithmetic, not assumed:**

| | as reported | valid-only basis | AAIR |
|---|---|---|---|
| Day-0 composite | 5/256 = 1.95 | 5/250 = 2.00 | **2 → 2 (unchanged)** |
| Day-0 Mirror tier | 5/160 = 3.12 | 5/158 = 3.16 | **3 → 3 (unchanged)** |
| Day-0 SLM tier | 0/96 = 0 | 0/92 = 0 | **0 → 0 (unchanged)** |

The numerator was **zero** at Day-0 for SLM, so the denominator choice never mattered *then*. It matters enormously at Day-7, when the numerator is not zero. **We can adopt the honest rule without touching the frozen baseline.** Day-0 is restated on the valid-only basis as *additional* fields (`*_valid_basis`) in `clients/b9/baselines/b9-day0-2026-07-14.json`; the original numbers are preserved and never overwritten, so the frozen artifact remains byte-comparable to what was published.

**Nothing else about the ruler moves.** No prompt, no model, no scoring logic changed — only denominator counting, retry/backoff, and the `status` field. Restating Day-0 must yield composite 2 and SLM 0; anything else means the artifact was misread and the work stops.

**Honest note on how this was found.** The first diagnosis was *wrong*: the daily rescore was accused of scoring 429s as absence. It was already excluding them (10/41). The real defect was the **inconsistency between the two instruments**, found only by counting the arrays instead of trusting the summary fields. Recorded here because it is the same failure the Cognitive Complacency piece is about — reading the summary instead of the source.

**Judge-facing upside:** "we exclude no-reads and publish the count" is a stronger sentence than silence. It is the frozen-ruler discipline applied to its own edge case.

---

### 2026-07-15 (Wed) — Single-number NAP enforcement + duplicate-record discovery. Verified live.

**Decision in force:** publish **(904) 272-3395 as the only number across the web.** 888-460-1308 remains an active toll-free line but is *unpublished* everywhere. Rationale: two authoritative numbers is an unresolvable conflict for entity resolution — a model has no basis to pick, so both are discounted. One number is worth more than two correct ones.

**Upstream emitter killed (the root cause).** Snippet **9071** (`Organization & Service JSON-LD Schema`) was still emitting a *second* `ContactPoint` with `+1-888-460-1308` inside the `#localbusiness` node — lines 51–57. This survived the 7/14 pass because 7/14 only fixed *prose and address* fields; the secondary ContactPoint was deliberate at the time. Removed the array element; fixed the trailing comma on the preceding entry.
- Verified against a cache-busted live fetch: `888-460-1308` occurrences **1 → 0**; `(888)` occurrences **0**; `904-272-3395` **6**; `block 8 LocalBusiness telephones = ['+1-904-272-3395','+1-904-272-3395']`; **all 27 JSON-LD blocks still parse, 0 errors.**
- **Why this matters more than any directory fix:** we were cleaning downstream listings while our own schema kept re-asserting the 888 as authoritative. Directories and crawlers re-ingest from the site. Every directory correction was going to decay back until this block died. This is the difference between a fix and a treadmill.

**False lead ruled out.** "Kingsley" appears 2× on the homepage — both are the *Florida Heritage Files* editorial series (Kingsley Plantation), not the address. **We have never published 985 Kingsley.** That address is purely third-party pollution, which means it entered via a data aggregator, not from us — so the aggregator layer (still the open item) is the true source.

**Chamber of Commerce — duplicate entity discovered (higher-value than the wrong address).** chamberofcommerce.com carries **two** Brand 9 records:
- `Brand 9 Signs` — 985 Kingsley Ave · 888-460-1308 · **28 reviews** · listing ID 2017564305 (wrong on both NAP fields)
- `Brand 9` — 1970 Solomon St · (904) 272-3395 · **26 reviews** (already correct)

A duplicate is worse than a wrong record: it splits review equity (28/26 instead of 54) and gives engines two conflicting entities under one name. Correction + **merge** requested via (a) the on-site dispute form and (b) email to `support@chamberofcommerce.com` (address verified from their own privacy policy mailto, not guessed). Both ask for a single record on the correct NAP, retaining reviews from both. **Chamber's own site search does not surface either listing** (returns honeypot filler rows), so the record is indexed-but-unsearchable — Bing surfaces it on page one regardless.

**Bing entity panel (diagnostic, no action yet):** address/phone/website already correct — the 7/14 site fixes propagated. Two residual defects: category reads **"Retail"** (GBP says *Sign shop*) and the About blurb still ends `Call (888)…`. Bing also grounds its rating on **Yellowpages 4.6/5 (9 reviews)** rather than GBP **4.8/57** — a review-surface gap, not a NAP gap. Bing matters disproportionately: **ChatGPT-search grounds on it**, and it is a Mirror-tier engine in the AAIR denominator.

**Honest expectation for the 2026-07-17 scan:** still foundation, not lift. Removing the 888 conflict raises the *ceiling* on entity resolution; it does not itself create corroboration. Expect SLM to stay ~0 (parametric tier cannot see any of this). Any movement remains Mirror-tier only. **The unpublished-888 change should produce no visible score delta on 7/17** — its payoff is that subsequent citation work stops decaying.

**Still not started (the levers that actually move the score):** review drive, remaining citation layer, data aggregators (the real 985 Kingsley source), Wikidata.

---

### 2026-07-14 (Tue) — Week-1 foundation. Verified live; all changes below were confirmed against the live page, not self-reported.

**NAP consistency (the #1 suppressor per `B9_Jacksonville_SEO_fix.md`)**
- Site-wide primary phone **888-460-1308 → (904) 272-3395** (matches GBP; 888 demoted to toll-free secondary). Verified: `has904=true / has888=false` on `/`, `/signage-jacksonville/`, and both new pages. — **SUPERSEDED 2026-07-15:** "888 as secondary" was reversed in favour of a single published number everywhere. The 888 line is still *active*; it is simply no longer *published*. See the 2026-07-15 entry.
- Entity schema address was **missing `streetAddress` and `postalCode` entirely** and named the wrong city. Now the GBP-exact **1970 Solomon St, Orange Park, FL 32073**. Verified: `addressLocality = ["Orange Park","Orange Park","Orange Park"]` (was `["Orange Park","Jacksonville","Orange Park"]` — a live self-contradiction).
- Removed the false "headquartered in Jacksonville" claim from the entity schema description. **Note:** the same phrase intentionally remains in *prose* on `/homebuilder-signage-florida/` — decision: Jacksonville stays in copy + `areaServed`, Orange Park in every `PostalAddress`.

**Entity schema**
- Snippet 9071 was declaring `['Organization','LocalBusiness']` on `@id .../#organization` — **colliding with Yoast's own `#organization`**. Now a clean `LocalBusiness` at `#localbusiness` with `parentOrganization` → Yoast. All 20 Services preserved.
- Snippet 9346's duplicate entity block removed (ProfessionalService node gone). **Still open:** 2 residual duplicates — an Organization+AggregateRating node and a second LocalBusiness also claiming `#localbusiness`. Assessed as low-impact hygiene; not expected to affect this scan.

**`/llms.txt`** — was returning **242KB of `text/html`** via a 301 to a WP page (it 200'd, so it passed a status check while failing its actual job). Root cause: Redirection plugin rule ID 162 overriding an already-correct `text/plain` emitter. Now: **200, `text/plain`, 6,289 bytes, no redirect.**

**`/signage-jacksonville/`** — H1 → exact-match "Sign Company in Jacksonville, FL"; added first-100-words entity sentence ("Brand 9 Signs is a sign company serving Jacksonville, FL since 1986"); added LocalBusiness/Service + FAQPage schema.

**Two answer-shaped pages published** (fast-clock bet):
- `/homebuilder-signage-company/` — title 59ch, meta desc 150ch, keyphrase "homebuilder signage company"
- `/community-monument-sign-cost/` — title 65ch, meta desc 154ch, keyphrase "community monument sign cost" (ballpark pricing approved as-is)
- Both shipped with **no meta description and doubled titles** ("… | Brand 9 Signs | Brand 9"); both fixed.
- **Both were invisible to Google at 2026-07-14 21:0x:** GSC reported *"URL is unknown to Google"* — never crawled, no referring page, no sitemap reference. Fixed via: indexing requested (priority queue), sitemap resubmitted (`sitemap_index.xml` had last been read **Jul 11**, before these pages existed), and internal links added from `/homebuilder-signage-florida/` with exact-match anchors.

**Honest expectation for the 2026-07-17 scan:** this is **foundation, not lift.** It removes reasons for engines to ignore B9; it does not create corroboration. The parametric majority (GPT-4o, Claude, Llama, Qwen, Grok, and the SLM tier) **cannot see any of this** — they answer from training weights, so SLM should stay ~0. Any movement should appear on the **Mirror/retrieval tier only** (Perplexity, ChatGPT-search, Gemini-grounded), and only if the new pages get crawled in time. **A large AAIR jump on 7/17 should be treated as a ruler problem, not a result.**

**Not yet started (the levers that actually move the score):** review drive, citation layer (Yelp, BBB, Angi, Nextdoor, Thumbtack, Houzz, Chamber), Wikidata entry. Per the Two-Clocks playbook these are what move the retrieval tier now and seed the parametric tier later. Blocked on account access / real customer outreach.

### Reference: generic local query (not B9's real market)
Kept for context only — B9 doesn't target this. business = "Brand 9 Signs", city = "Orange Park, FL", service = "custom signs".

| Date | AAIR /100 | Mirror | SLM | Fraction | Notes |
|------|-----------|--------|-----|----------|-------|
| 2026-07-13 | 0 | 0 | 0 | 0/96 | Invisible on generic local signage queries. |
