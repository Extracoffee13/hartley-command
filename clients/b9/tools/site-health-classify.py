#!/usr/bin/env python3
"""
B9 Site-Health classifier — consumes the in-browser collector output and produces the
site-health report the dashboard + knowledge graph read. Dependency-free (stdlib).

Input : a JSON array of per-page collector results (from collector.js), via --in <file> or stdin:
        [{"page":"/portfolio/","checked":102,"broken":[{"url","status","type"}],"good_imgs":[...]}, ...]
Output: site-health-assets.json with by_status, classifications, and SAFE auto-repair proposals.

SAFETY POLICY (matches the flywheel's autonomy guardrails):
  - AUTO-REPAIR only the safe class: a broken <img> that has a verified-200 image on the SAME page ->
    propose repoint (reversible, in-context). Emitted as auto_safe=true proposals for the deploy step.
  - FLAG-ONLY the risky class: a batch of uploads images sharing 410 = a redirect/.htaccess rule
    regression. NEVER auto-edit .htaccess; surface it high-severity for a scoped human/Hermes fix.
"""
import sys, json, argparse

ap = argparse.ArgumentParser()
ap.add_argument("--in", dest="inp", default=None)
ap.add_argument("--out", default="site-health-assets.json")
ap.add_argument("--asof", default="")
args = ap.parse_args()

raw = open(args.inp).read() if args.inp else sys.stdin.read()
pages = json.loads(raw)
if isinstance(pages, dict):
    pages = [pages]

broken = []       # flattened, with page context
good_by_page = {}
for pg in pages:
    good_by_page[pg["page"]] = pg.get("good_imgs", [])
    for b in pg.get("broken", []):
        broken.append({**b, "page": pg["page"]})

by_status = {}
for b in broken:
    by_status[str(b["status"])] = by_status.get(str(b["status"]), 0) + 1

img_410 = [b for b in broken if b["type"] == "image" and b["status"] == 410 and "/uploads/" in b["url"]]
img_404 = [b for b in broken if b["type"] == "image" and b["status"] == 404]
asset_5xx = [b for b in broken if b["status"] and b["status"] >= 500]

classifications = []
if len(img_410) >= 5:
    classifications.append({
        "kind": "rule_regression", "severity": "high", "action": "FLAG_ONLY",
        "count": len(img_410),
        "detail": "Many legit /wp-content/uploads images return 410 Gone — an over-broad redirect/.htaccess rule, not missing files. Breaks images site-wide. Do NOT auto-edit .htaccess; needs a scoped rule fix (add a RewriteCond exempting /wp-content/uploads) + verify 200.",
        "sample": sorted({b["url"] for b in img_410})[:10],
    })
if img_404:
    classifications.append({
        "kind": "missing_file", "severity": "medium", "action": "REPOINT_OR_RESTORE",
        "count": len(img_404), "detail": "Images 404 — file gone. Repoint to a verified in-page replacement or restore the file.",
        "sample": sorted({b["url"] for b in img_404})[:10],
    })
if asset_5xx:
    classifications.append({"kind": "server_error", "severity": "high", "action": "FLAG_ONLY",
        "count": len(asset_5xx), "detail": "Assets returning 5xx — origin/server error.",
        "sample": sorted({b["url"] for b in asset_5xx})[:10]})

# SAFE auto-repair proposals: broken <img> on a page that has a verified-200 image on the same page
proposals = []
seen = set()
for b in broken:
    if b["type"] != "image":
        continue
    goods = good_by_page.get(b["page"], [])
    key = (b["page"], b["url"])
    if goods and key not in seen:
        seen.add(key)
        proposals.append({"page": b["page"], "broken": b["url"], "status": b["status"],
                          "safe_replacement": goods[0], "auto_safe": True,
                          "note": "Repoint only if the broken URL is a genuinely-missing file; if it is a rule_regression (above), fix the rule instead — do not mask it by repointing."})

report = {
    "generated": args.asof, "source": "b9-site-health-sentinel",
    "pages_scanned": len(pages),
    "assets_checked": sum(p.get("checked", 0) for p in pages),
    "broken_count": len(broken),
    "by_status": by_status,
    "broken": sorted(broken, key=lambda b: (b["type"], -(b["status"] or 0), b["url"])),
    "classifications": classifications,
    "proposed_repairs": proposals,
    "health": "green" if not broken else ("red" if any(c["severity"] == "high" for c in classifications) else "amber"),
}
json.dump(report, open(args.out, "w"), indent=1)
print(f"[b9-health] pages={report['pages_scanned']} assets={report['assets_checked']} broken={report['broken_count']} health={report['health']}")
for c in classifications:
    print(f"[b9-health] {c['action']} [{c['severity']}] {c['kind']} x{c['count']}")
print(f"[b9-health] safe repoint proposals: {len(proposals)} | wrote {args.out}")
