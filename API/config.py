import os, json, re

COMPILERS = {
    "c": {"compiler": "gcc", "extension": ".c"},
    "cpp": {"compiler": "g++", "extension": ".cpp"},
    "java": {"compiler": "javac", "extension": ".java"},
    "python": {"interpreter": "python", "extension": ".py"},
    "javascript": {"interpreter": "node", "extension": ".js"},
}

TEST_CASES_ROOT_DIR = "tests"

def validate_code(lang: str, code: str, rules: dict) -> bool:
    patterns = rules.get(lang, [])
    return all(re.search(p, code) for p in patterns)

def loadTest(qid: str) -> dict:
    qpath = os.path.join(TEST_CASES_ROOT_DIR, str(qid))
    if not os.path.isdir(qpath):
        raise FileNotFoundError(f"Question directory not found: {qpath}")

    data = {"timeout": 5, "test_pairs": [], "templates": {}}
    cfg_path = os.path.join(qpath, "config.json")

    if os.path.exists(cfg_path):
        try:
            with open(cfg_path, encoding="utf-8") as f:
                cfg = json.load(f)
                data["timeout"] = cfg.get("timeout", 5)
                data["templates"] = cfg.get("templates", {})
                data["rules"] = cfg.get("rules", {})
        except json.JSONDecodeError:
            print(f"Warning: invalid JSON in {cfg_path}. Using default timeout.")
    else:
        print(f"Warning: config.json not found for {qid}. Using default timeout.")

    ins, outs = {}, {}
    for fn in os.listdir(qpath):
        m = re.match(r'^(\d+)\.(in|out)$', fn)
        if not m: 
            continue
        with open(os.path.join(qpath, fn), encoding="utf-8") as f:
            (ins if m.group(2) == "in" else outs)[m.group(1)] = f.read()

    nums = sorted(set(ins) | set(outs), key=int)
    for n in nums:
        if n not in outs:
            raise ValueError(f"Missing {n}.out for question {qid}")
        data["test_pairs"].append({
            "test_number": n,
            "input": ins.get(n, ""),
            "expected_output": outs[n]
        })

    if not data["test_pairs"]:
        raise FileNotFoundError(f"No test pairs found for {qid}")
    return data
