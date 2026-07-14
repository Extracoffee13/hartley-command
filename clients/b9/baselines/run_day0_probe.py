#!/usr/bin/env python3
import concurrent.futures, datetime, json, os, pathlib, re, time, urllib.error, urllib.request

HOME = pathlib.Path.home()
ENV_FILE = HOME / ".hermes" / ".env"
OUT_DIR = pathlib.Path("/Users/alfredpennyworth/AP-v2/_RECOVERED_2026-06-24/hartley-command/clients/b9/baselines")
OUT_JSON = OUT_DIR / "b9-day0-2026-07-14.json"

api_key = ""
if ENV_FILE.exists():
    for line in ENV_FILE.read_text().splitlines():
        if line.startswith("OPENROUTER_API_KEY="):
            api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
            break

if not api_key:
    raise SystemExit(1)

ENGINES = [
    {"key": "gpt4o",        "label": "ChatGPT (GPT-4o)",              "model": "openai/gpt-4o"},
    {"key": "gpt4omini",    "label": "ChatGPT (GPT-4o mini)",         "model": "openai/gpt-4o-mini"},
    {"key": "claudesonnet", "label": "Claude Sonnet 4.5",             "model": "anthropic/claude-sonnet-4.5"},
    {"key": "claudehaiku",  "label": "Claude Haiku 4.5",              "model": "anthropic/claude-haiku-4.5"},
    {"key": "gemini",       "label": "Google Gemini 2.5",             "model": "google/gemini-2.5-flash"},
    {"key": "perplexity",   "label": "Perplexity (Sonar)",            "model": "perplexity/sonar"},
    {"key": "grok",         "label": "xAI Grok 4.5",                  "model": "x-ai/grok-4.5"},
    {"key": "deepseek",     "label": "DeepSeek V3.1",                 "model": "deepseek/deepseek-chat-v3.1"},
    {"key": "llama4",       "label": "Llama 4 Maverick",              "model": "meta-llama/llama-4-maverick"},
    {"key": "qwen72b",      "label": "Qwen 2.5 72B",                  "model": "qwen/qwen-2.5-72b-instruct"},
    {"key": "llama3b",      "label": "Llama 3.2 3B",                  "model": "meta-llama/llama-3.2-3b-instruct"},
    {"key": "llama8b",      "label": "Llama 3.1 8B",                  "model": "meta-llama/llama-3.1-8b-instruct"},
    {"key": "gemma4b",      "label": "Gemma 3 4B",                    "model": "google/gemma-3-4b-it"},
    {"key": "phi4",         "label": "Microsoft Phi-4",               "model": "microsoft/phi-4"},
    {"key": "qwen7b",       "label": "Qwen 2.5 7B",                   "model": "qwen/qwen-2.5-7b-instruct"},
    {"key": "ministral8b",  "label": "Ministral 8B",                  "model": "mistralai/ministral-8b-2512"},
]
MIRROR_KEYS = {"gpt4o","gpt4omini","claudesonnet","claudehaiku","gemini","perplexity","grok","deepseek","llama4","qwen72b"}

PROMPTS = [
    {"category": "emergency/near-me", "prompt": "emergency sign repair near me"},
    {"category": "emergency/near-me", "prompt": "24 hour sign repair Orange Park FL"},
    {"category": "best sign company", "prompt": "best sign company Jacksonville FL"},
    {"category": "best sign company", "prompt": "best sign company Orange Park FL"},
    {"category": "commercial/general", "prompt": "commercial sign company Jacksonville FL"},
    {"category": "commercial/general", "prompt": "custom business signs Orange Park FL"},
    {"category": "monument/homebuilder", "prompt": "monument signs Jacksonville FL"},
    {"category": "monument/homebuilder", "prompt": "monument sign company Orange Park FL"},
    {"category": "monument/homebuilder", "prompt": "home builder signage company Jacksonville FL"},
    {"category": "monument/homebuilder", "prompt": "model home display signs Orange Park FL"},
    {"category": "monument/homebuilder", "prompt": "community development signs Jacksonville FL"},
    {"category": "wayfinding/egd", "prompt": "wayfinding signage company Jacksonville FL"},
    {"category": "commercial/general", "prompt": "construction site signs installation Jacksonville FL"},
    {"category": "wayfinding/egd", "prompt": "environmental graphic design firm Orange Park FL"},
    {"category": "military/government", "prompt": "military base signage contractor Jacksonville FL"},
    {"category": "emergency/near-me", "prompt": "sign installation near me"},
]

COMPETITORS = ["FastSigns", "Signarama", "SpeedPro", "Image360"]
ENTITY_NAMES = ["Brand 9 Signs", "Brand 9", "brand9signs.com", "brand9signs"]
ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"

def ask_model(model_slug, question):
    payload = json.dumps({"model": model_slug, "messages": [{"role": "user", "content": question}], "max_tokens": 250, "temperature": 0.2}).encode()
    headers = {"Content-Type": "application/json", "Authorization": "Bearer " + api_key, "HTTP-Referer": "https://prag-ma.ai", "X-Title": "PRAGMA AAIR Day-0"}
    req = urllib.request.Request(ENDPOINT, data=payload, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            data = json.loads(resp.read().decode("utf8"))
        choices = data.get("choices", [])
        if not choices: return None, "no choices"
        return choices[0].get("message", {}).get("content", ""), None
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}: {e.read().decode('utf8', errors='ignore')[:200]}"
    except Exception as e:
        return None, str(e)[:200]

def retry_ask(model_slug, question, max_retries=1):
    for attempt in range(max_retries + 1):
        content, err = ask_model(model_slug, question)
        if content is not None:
            return content, None
        if err and ("429" in err or "rate" in err.lower()):
            time.sleep(2 ** attempt)
        else:
            break
    return None, err

def contains(text, names):
    if not text: return False
    low = text.lower()
    return any(n.lower() in low for n in names)

def blurb(text, names):
    if not text: return ""
    low = text.lower()
    for n in names:
        pos = low.find(n.lower())
        if pos >= 0:
            s = max(0, pos - 120); e = min(len(text), pos + len(n) + 120)
            return text[s:e].replace("\n", " ")
    return text[:240].replace("\n", " ")

results = []
def worker(args):
    e, p_idx, p = args
    answer, err = retry_ask(e["model"], p["prompt"])
    if answer is None:
        return {"engine_key": e["key"], "engine_label": e["label"], "tier": "mirror" if e["key"] in MIRROR_KEYS else "slm", "prompt_index": p_idx, "prompt": p["prompt"], "category": p["category"], "named_b9": False, "cited_competitors": {c: False for c in COMPETITORS}, "answer_truncated": "", "error": err}
    return {"engine_key": e["key"], "engine_label": e["label"], "tier": "mirror" if e["key"] in MIRROR_KEYS else "slm", "prompt_index": p_idx, "prompt": p["prompt"], "category": p["category"], "named_b9": contains(answer, ENTITY_NAMES), "cited_competitors": {c: contains(answer, [c]) for c in COMPETITORS}, "answer_truncated": blurb(answer, ENTITY_NAMES + COMPETITORS), "error": None}

tasks = [(e, p_idx, p) for p_idx, p in enumerate(PROMPTS) for e in ENGINES]
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
    for i, res in enumerate(ex.map(worker, tasks)):
        results.append(res)
        if (i + 1) % 16 == 0:
            print(f"  {i+1}/{len(tasks)}", flush=True)

total_cells = len(PROMPTS) * len(ENGINES)
b9_hits = sum(1 for r in results if r["named_b9"])
aair_pct = round(100.0 * b9_hits / total_cells)
mirror_hits = sum(1 for r in results if r["tier"] == "mirror" and r["named_b9"]); mirror_total = sum(1 for r in results if r["tier"] == "mirror")
slm_hits = sum(1 for r in results if r["tier"] == "slm" and r["named_b9"]); slm_total = sum(1 for r in results if r["tier"] == "slm")

prompt_rows = []
for p_idx, p in enumerate(PROMPTS):
    prs = [r for r in results if r["prompt_index"] == p_idx]
    named_any = sum(1 for r in prs if r["named_b9"])
    named_mirror = sum(1 for r in prs if r["tier"] == "mirror" and r["named_b9"])
    named_slm = sum(1 for r in prs if r["tier"] == "slm" and r["named_b9"])
    comp_counts = {c: sum(1 for r in prs if r["cited_competitors"].get(c)) for c in COMPETITORS}
    prompt_rows.append({"index": p_idx, "category": p["category"], "prompt": p["prompt"], "named_any": named_any, "named_mirror": named_mirror, "named_slm": named_slm, "competitor_hits": comp_counts})

tier1_presence_count = sum(1 for row in prompt_rows if row["named_mirror"] > 0)

engine_rows = []
for e in ENGINES:
    ers = [r for r in results if r["engine_key"] == e["key"]]
    hits = sum(1 for r in ers if r["named_b9"])
    engine_rows.append({"key": e["key"], "label": e["label"], "tier": "mirror" if e["key"] in MIRROR_KEYS else "slm", "hits": hits, "total": len(PROMPTS), "pct": round(100.0 * hits / len(PROMPTS)), "per_prompt_named": [bool(next((r for r in ers if r["prompt_index"] == p_idx), {}).get("named_b9")) for p_idx in range(len(PROMPTS))]})

citing_surfaces = [er["label"] for er in engine_rows if er["hits"] > 0]

comp_tier1_counts = {}
for c in COMPETITORS:
    comp_tier1_counts[c] = sum(1 for p_idx, p in enumerate(PROMPTS) if any(r["cited_competitors"].get(c) for r in results if r["prompt_index"] == p_idx and r["tier"] == "mirror"))
top2 = sorted(comp_tier1_counts.items(), key=lambda x: (-x[1], x[0]))[:2]

errors = [{"engine": r["engine_key"], "prompt_index": r["prompt_index"], "error": r["error"]} for r in results if r["error"]]
now = datetime.datetime.utcnow().isoformat() + "Z"

payload = {
    "baseline_meta": {"label": "Brand 9 Signs Day-0 AAIR baseline", "date": "2026-07-14", "source": "Deep local 16-engine x 16-prompt OpenRouter probe (frozen panel)", "business": "Brand 9 Signs", "domain": "brand9signs.com", "primary_geo": ["Jacksonville, FL", "Orange Park, FL"], "prompt_set_version": "b9-high-intent-v1", "disclaimer": "Measurement only — no site content changed.", "generated_at": now},
    "summary": {"composite_aair_0_100": aair_pct, "named_cells": b9_hits, "total_cells": total_cells, "fraction": f"{b9_hits}/{total_cells}", "tier1_presence_count": tier1_presence_count, "any_presence_count": sum(1 for row in prompt_rows if row["named_any"] > 0), "prompt_count": len(PROMPTS)},
    "tier_subtotals": {"mirror_cloud": {"hits": mirror_hits, "total": mirror_total, "pct": round(100.0 * mirror_hits / mirror_total) if mirror_total else 0}, "slm_on_device": {"hits": slm_hits, "total": slm_total, "pct": round(100.0 * slm_hits / slm_total) if slm_total else 0}},
    "per_engine": engine_rows,
    "per_prompt": prompt_rows,
    "surfaces_citing_b9": citing_surfaces,
    "competitor_tier1_counts": comp_tier1_counts,
    "top_2_competitor_tier1_counts": [{"competitor": c, "tier1_prompt_presence": n} for c, n in top2],
    "errors": errors,
    "detailed_matrix": results,
}
OUT_JSON.write_text(json.dumps(payload, indent=2))
print(f"FINAL: AAIR={aair_pct}% Mirror={mirror_hits}/{mirror_total} SLM={slm_hits}/{slm_total} Tier1={tier1_presence_count}/{len(PROMPTS)} Citing={citing_surfaces} Top2={top2} Errors={len(errors)}")
