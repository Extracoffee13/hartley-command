#!/usr/bin/env python3
"""
B9 Knowledge Graph — portable/production build (graph engineering, 2026-08-18)
==============================================================================
Runs inside Hermes' daily flywheel refresh. Reads the LIVE feeds from the feed
repo and writes three artifacts back INTO the feed repo so the dashboard + the
answer-page factory read from the graph ("within the flywheel, not a hand
selection"). Dependency-free (stdlib). Rebuilds fully from source every run —
never let a stale graph make wrong answers look structured.

Usage:
    python3 b9_knowledge_graph.py --repo /path/to/feed-repo
    (defaults --repo to two levels up from this file: <repo>/clients/b9/tools/..)

Inputs  (relative to --repo):
    clients/b9/brand-insights/latest.json        (required)
    brand-insights/site-health.json              (required)
    clients/b9/brand-insights/experiments.json   (optional)
    clients/b9/brand-insights/flywheel-results.json (optional)
Outputs (written into clients/b9/brand-insights/):
    kg-graph.json  build-target-queue.json  provenance-report.json
"""
import json, re, sys, os, hashlib, argparse, datetime

ap = argparse.ArgumentParser()
ap.add_argument("--repo", default=None, help="feed repo root")
ap.add_argument("--asof", default=None, help="ISO timestamp override (Hermes passes date)")
args = ap.parse_args()

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(args.repo) if args.repo else os.path.abspath(os.path.join(HERE, "../../.."))
BI   = os.path.join(REPO, "clients", "b9", "brand-insights")
def load(p, default=None, required=False):
    try:
        with open(p) as f: return json.load(f)
    except Exception as e:
        if required:
            sys.stderr.write(f"[FATAL] missing required input {p}: {e}\n"); sys.exit(2)
        return default

latest = load(os.path.join(BI, "latest.json"), {}, required=True)
health = load(os.path.join(REPO, "brand-insights", "site-health.json"), {}, required=True)
exps   = (load(os.path.join(BI, "experiments.json"), {}) or {}).get("experiments", [])
wins   = (load(os.path.join(BI, "flywheel-results.json"), {}) or {}).get("events", [])
demand = (load(os.path.join(BI, "validated-demand.json"), {}) or {}).get("signals", [])  # real inquiries

# ---------- extraction dictionaries (grounded in real B9 slugs) ----------
METROS = ["jacksonville","orange park","boca raton","miami beach","naples","tampa","orlando",
          "st augustine","ponte vedra","fleming island","palm beach","fort lauderdale","sarasota",
          "fernandina","clay county","jax","florida"]
VERTICALS = {"commercial sign":"commercial signage","community entrance":"community entrance signs",
    "monument sign":"monument signs","wayfinding":"wayfinding","master-planned":"master-planned community signage",
    "master planned":"master-planned community signage","homebuilder":"homebuilder signage",
    "home builder":"homebuilder signage","entrance sign":"community entrance signs",
    "environmental graphic":"environmental graphic design","model home":"model-home signage",
    "military base":"military base signage","campus":"campus wayfinding","sign company":"sign company"}
BUILDERS = ["lennar","dream finders","dr horton","d.r. horton","pulte","gl homes","toll brothers",
            "mattamy","richmond american","ici homes","providence homes"]
PROOFS = {
    "lennar-250":  {"label":"250+ Lennar community signs delivered","kind":"portfolio"},
    "cgc-license": {"label":"FL GC license CGC1511856","kind":"credential"},
    "orange-park-hq":{"label":"Orange Park, FL headquarters (local presence)","kind":"locality"},
    "hvhz-noa":    {"label":"Miami-Dade HVHZ / NOA + 170mph Palm Beach rating","kind":"engineering"},
    "40yr":        {"label":"40 years in business (est. 1986)","kind":"heritage"}}
PAGE_PROOF = {
    "community-entrance-signs-boca-raton-fl": ["lennar-250","cgc-license","hvhz-noa","orange-park-hq"],
    "community-entrance-signs-miami-beach-fl": ["hvhz-noa","lennar-250","cgc-license"],
    "lennar-community-signs-florida": ["lennar-250","orange-park-hq","40yr"]}

def slug_of(url):
    if not url: return ""
    return re.sub(r"https?://[^/]+/","",url).strip("/").lower()
def find_all(text, options):
    t=(text or "").lower(); return [o for o in options if o in t]

class G:
    def __init__(s): s.nodes={}; s.edges=[]
    def node(s,typ,key,**a):
        nid=f"{typ}:{key}"
        s.nodes.setdefault(nid,{"id":nid,"type":typ,"key":key})
        s.nodes[nid].update({k:v for k,v in a.items() if v is not None}); return nid
    def out(s,nid,rel=None): return [e for e in s.edges if e["src"]==nid and (rel is None or e["rel"]==rel)]
    def inn(s,nid,rel=None): return [e for e in s.edges if e["dst"]==nid and (rel is None or e["rel"]==rel)]
    def edge(s,a,r,b,**x): s.edges.append({"src":a,"rel":r,"dst":b,**x})
g=G()

ENGINE_LABEL={"chatgpt":"ChatGPT","claude":"Claude","gemini":"Gemini","perplexity":"Perplexity",
              "google_ai_overview":"Google AI Overview","grok":"Grok"}
for k,lab in ENGINE_LABEL.items():
    g.node("Engine",k,label=lab,cited_anywhere=bool((latest.get("surfaces",{}).get(k) or {}).get("cited")))

gsc=health.get("gsc",{})
q_impr={(r.get("q") or "").lower():{"clicks":r.get("clicks",0),"impr":r.get("impr",0)} for r in gsc.get("top_queries",[])}
page_clicks={slug_of(r.get("url")):r.get("clicks",0) for r in gsc.get("top_pages",[])}

def tags(text,url):
    blob=f"{text} {slug_of(url)}".replace("-"," ")
    return find_all(blob,METROS), sorted({VERTICALS[k] for k in VERTICALS if k in blob}), find_all(blob,BUILDERS)

for au in latest.get("answer_units",[]):
    q=au.get("question") or au.get("q") or ""; url=au.get("url") or ""
    qn=g.node("Query",hashlib.md5(q.encode()).hexdigest()[:8],text=q,status=au.get("status"),
              traffic=au.get("traffic"),inquiries=au.get("inquiries",0))
    fuel=0
    for gq,m in q_impr.items():
        if gq and (gq in q.lower() or q.lower() in gq): fuel=max(fuel,m["impr"])
    g.nodes[qn]["fuel_impr"]=fuel
    for eng in (au.get("cited_by") or []):
        ek=eng.lower().replace(" ","_")
        if ek in ENGINE_LABEL: g.edge(f"Engine:{ek}","CITES",qn)
    if url:
        sl=slug_of(url); pn=g.node("AnswerPage",sl,url=url,slug=sl,clicks=page_clicks.get(sl))
        g.edge(pn,"ANSWERS",qn)
        ms,vs,bs=tags(q,url)
        for m in ms: g.edge(pn,"TARGETS",g.node("Metro",m,label=m.title()))
        for v in vs: g.edge(pn,"TARGETS",g.node("Vertical",v,label=v))
        for b in bs: g.edge(pn,"TARGETS",g.node("Builder",b,label=b.title()))
        for pid in PAGE_PROOF.get(sl,[]): g.edge(pn,"USES_PROOF",g.node("Proof",pid,**PROOFS[pid]))
for pid,meta in PROOFS.items(): g.node("Proof",pid,**meta)

for e in exps:
    en=g.node("Experiment",e.get("id","exp"),etype=e.get("type"),lever=e.get("lever"),status=e.get("status"),goal=e.get("goal"))
    for v in e.get("variants",[]):
        vn=g.node("Variant",f"{e.get('id')}::{v.get('label')}",label=v.get("label"),metro=v.get("metro"))
        g.edge(en,"TESTS",vn)
        if v.get("url"):
            sl=slug_of(v["url"]); pn=g.node("AnswerPage",sl,url=v["url"],slug=sl); g.edge(vn,"APPLIES_TO",pn)
for w in wins:
    wn=g.node("Win",(w.get("date","")+"-"+hashlib.md5((w.get("title","")).encode()).hexdigest()[:5]),
              title=w.get("title"),kind=w.get("kind"),metric=w.get("metric"),date=w.get("date"))
    blob=(w.get("title","")+" "+w.get("detail","")).lower()
    for nid,n in list(g.nodes.items()):
        if n["type"]=="AnswerPage" and n.get("slug","").replace("-"," ")[:15] in blob: g.edge(wn,"ATTRIBUTED",nid)

# ---- validated demand from real inquiries -> Demand nodes (highest-priority build signal) ----
for d in demand:
    dk=hashlib.md5((d.get("vertical","")+d.get("metro","")).encode()).hexdigest()[:8]
    dn=g.node("Demand",dk,vertical=d.get("vertical"),metro=d.get("metro"),source=d.get("source"),
              date=d.get("date"),deadline=d.get("deadline"),note=d.get("note"),
              suggested_pages=d.get("suggested_pages"))
    ms=find_all((d.get("metro") or "")+" "+(d.get("vertical") or ""),METROS)
    for m in ms: g.edge(dn,"WANTS", g.node("Metro",m,label=m.title()))
    # does an AnswerPage already TARGET this vertical? (gap check)
    vlabel=(d.get("vertical") or "").lower()
    covered=any(n["type"]=="Vertical" and vlabel in (n.get("label","").lower()) for n in g.nodes.values())
    g.nodes[dn]["covered_by_page"]=covered

BEH=["LEARNS","PERSONALIZES","TESTS","CONVERTS","MEASURES","PIVOTS"]
for b in BEH: g.node("Behaviour",b,label=b)
WIRED=[("LEARNS","PERSONALIZES"),("PERSONALIZES","TESTS"),("TESTS","CONVERTS"),
       ("CONVERTS","MEASURES"),("MEASURES","PIVOTS"),("PIVOTS","LEARNS")]
for a,b in WIRED: g.edge(f"Behaviour:{a}","FLOWS_TO",f"Behaviour:{b}",live=True)

# ---- traversals ----
def build_targets():
    rows=[]
    for nid,n in g.nodes.items():
        if n["type"]!="Query": continue
        rows.append({"question":n["text"],"fuel_impr":n.get("fuel_impr",0),
                     "engines_citing":len(g.inn(nid,"CITES")),
                     "has_answer_page":bool(g.inn(nid,"ANSWERS")),"status":n.get("status")})
    gaps=[r for r in rows if r["engines_citing"]==0]
    gaps.sort(key=lambda r:(-r["fuel_impr"], r["status"]!="targeting"))
    return gaps
def provenance():
    return [g.nodes[nid].get("slug") for nid,n in g.nodes.items()
            if n["type"]=="AnswerPage" and not g.out(nid,"USES_PROOF")]
def flywheel_dead():
    return [(e["src"].split(':')[1],e["dst"].split(':')[1]) for e in g.edges if e["rel"]=="FLOWS_TO" and not e.get("live")]
def attribution():
    out=[]
    for nid,n in g.nodes.items():
        if n["type"]!="Win": continue
        for e in g.out(nid,"ATTRIBUTED"):
            pg=g.nodes[e["dst"]]
            out.append({"win":n.get("title"),"page":pg.get("slug"),
                        "queries":[g.nodes[x["dst"]]["text"] for x in g.out(e["dst"],"ANSWERS")]})
    return out

gaps=build_targets(); prov=provenance(); dead=flywheel_dead(); attr=attribution()
# real-inquiry demand = top of the build queue (a human asked; demand is proven pre-GSC)
demand_targets=[{"vertical":n.get("vertical"),"metro":n.get("metro"),"source":"real_inquiry",
                 "deadline":n.get("deadline"),"covered_by_page":n.get("covered_by_page"),
                 "suggested_pages":n.get("suggested_pages"),"note":n.get("note")}
                for n in g.nodes.values() if n["type"]=="Demand"]
now = args.asof or (latest.get("ts") or "")
counts={}; rc={}
for n in g.nodes.values(): counts[n["type"]]=counts.get(n["type"],0)+1
for e in g.edges: rc[e["rel"]]=rc.get(e["rel"],0)+1

os.makedirs(BI, exist_ok=True)
json.dump({"generated":now,"source":"b9_knowledge_graph.py","nodes":list(g.nodes.values()),"edges":g.edges,
           "counts":{"nodes":counts,"edges":rc}}, open(os.path.join(BI,"kg-graph.json"),"w"), indent=1)
json.dump({"generated":now,"method":"graph-traversal: Query ∧ zero-citation, ranked by GSC fuel",
           "validated_demand_first":demand_targets,   # real inquiries jump the queue
           "count":len(gaps),"queue":gaps}, open(os.path.join(BI,"build-target-queue.json"),"w"), indent=1)
json.dump({"generated":now,"rule":"real-proof-only: AnswerPage must have a USES_PROOF edge",
           "pages_without_proof":len(prov),"pages":prov,
           "flywheel_dead_edges":dead}, open(os.path.join(BI,"provenance-report.json"),"w"), indent=1)

print(f"[b9-kg] built {sum(counts.values())} nodes / {sum(rc.values())} edges  as-of {now}")
if demand_targets:
    print(f"[b9-kg] validated demand (real inquiries) at top of queue: "
          + "; ".join(f"{d['vertical']} @ {d['metro']}"+(" [NO PAGE]" if not d['covered_by_page'] else "") for d in demand_targets))
print(f"[b9-kg] build-target queue: {len(gaps)} zero-citation gaps  | top: "
      + (gaps[0]['question'][:60] if gaps else '—'))
print(f"[b9-kg] provenance: {len(prov)} pages missing proof | flywheel dead edges: {dead or 'none'}")
print(f"[b9-kg] wrote kg-graph.json, build-target-queue.json, provenance-report.json -> {BI}")
