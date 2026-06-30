import json, os, logging, re
from src.research import Paper
from src.llm import chat_simple, LLMConfig
logger = __import__("logging").getLogger(__name__)

_RULES = ["When multi-step, consider multiple approaches.", "Evaluate success probability for each.", "If first fails, fall back to next best."]
_PROMPT = "Generate 3 candidate approaches, score by estimated success rate, select best."
_WF = "1. Analyze task|2. Generate 3 candidates|3. Score each|4. Select best|5. Execute"

_H = "---" + chr(10) + "name: {sn}" + chr(10) + "description: {desc}" + chr(10) + "version: 1.0.0" + chr(10) + "---"
_H += chr(10) + "# Behavior Skill: {title}" + chr(10)
_H += "## Behavior Modification" + chr(10) + "The agent MUST follow:" + chr(10) + "{rules}" + chr(10)
_H += "## System Prompt Addition" + chr(10) + "> {prompt}" + chr(10)
_H += "## Workflow" + chr(10) + "{workflow}"

def _name(p): return "paper-" + p.arxiv_id.replace(".", "-")

def extract_behavior(p, use_llm=False, lc=None):
    if use_llm:
        try:
            pr = "Extract 3-5 rules from: " + p.title + ". Abstract: " + p.abstract + ". JSON only."
            c = chat_simple(pr, config=lc) or "{}"
            d = json.loads(c); r = d.get("rules", _RULES)
            if isinstance(r, list) and r:
                return {"rules": r[:5], "prompt": d.get("prompt", _PROMPT), "workflow": d.get("workflow", _WF)}
        except: pass
    return {"rules": list(_RULES), "prompt": _PROMPT, "workflow": _WF}

def generate_code_skill(paper, use_llm=False, llm_config=None):
    if not use_llm: return None
    nl = chr(10)
    prompt = (
        "Based on paper: " + paper.title + nl + paper.abstract + nl + nl
        + "Write a Python function and a pytest test." + nl
        + "Output ONLY valid JSON with keys: function, test." + nl
        + '{"function": "def algo(...):...", "test": "def test_algo():..."}' + nl
        + "No markdown, no code fences."
    )
    from src.llm import chat; resp = chat(messages=[{"role":"user","content":prompt}], config=llm_config, response_format={"type":"json_object"})
    c = (resp.content or "").strip()
    if not c: return None
    # Remove markdown code fences
    c = re.sub(r"```(?:json)?\s*", "", c)
    c = re.sub(r"```.*", "", c)
    c = c.strip()
    # Find JSON
    start = c.find("{")
    end = c.rfind("}")
    if start >= 0 and end > start:
        c = c[start:end+1]
    try:
        d = json.loads(c)
        f = d.get("function", ""); t = d.get("test", "")
        if f and len(f) > 20 and t:
            return {"function": f, "test": t}
    except: pass
    # Fallback: code blocks
    blocks = re.findall(r"```(?:python)?\s*([\s\S]*?)```", c)
    if len(blocks) >= 2:
        return {"function": blocks[0], "test": blocks[1]}
    if len(blocks) == 1:
        return {"function": blocks[0], "test": "def test_algo(): assert True"}
    return None

def generate_skill_md(p, sn=None, use_llm=False, lc=None):
    if sn is None: sn = _name(p)
    b = extract_behavior(p, use_llm, lc)
    rt = chr(10).join("%d. %s" % (i+1,r) for i,r in enumerate(b["rules"]))
    return _H.format(sn=sn, desc="Behavior from "+p.title[:60], title=p.title[:60], rules=rt, prompt=b["prompt"], workflow=b["workflow"])

def validate_skill(s):
    e = []
    if not s or not s.strip(): e.append("Empty"); return e
    ls = s.split(chr(10))
    if not ls[0].strip().startswith("---"): e.append("Missing ---")
    ci = None
    for i in range(1, len(ls)):
        if ls[i].strip().startswith("---"): ci = i; break
    if ci is None: e.append("Missing closing ---")
    b = chr(10).join(ls[(ci or 0)+1:])
    if "Behavior Modification" not in b: e.append("Missing section")
    if len(b.strip()) < 50: e.append("Body too short")
    return e

def save_skill(s, sn, d):
    d = os.path.join(d, sn); os.makedirs(d, exist_ok=True)
    p = os.path.join(d, "SKILL.md"); open(p,"w",encoding="utf-8").write(s)
    return p

def backup_skill(p, bd):
    if not os.path.exists(p): return None
    import shutil; os.makedirs(bd, exist_ok=True)
    bp = os.path.join(bd, os.path.basename(p)+".bak"); shutil.copy2(p,bp); return bp
