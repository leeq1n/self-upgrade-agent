# Sandbox: execute generated code in isolated subprocess.
import os, subprocess, tempfile, time, json

_T = chr(123) + chr(123) + chr(34) + "passed" + chr(34) + ": True" + chr(125) + chr(125)
_F = chr(123) + chr(123) + chr(34) + "passed" + chr(34) + ": False, " + chr(34) + "error" + chr(34) + ": str(e)}" + chr(125)

_TEMPLATE = """
import sys, json, traceback
{function_code}
{test_code}
def _run():
    try:
        {test_name}()
        print("SBOK" + json.dumps(dict(passed=True)))
    except AssertionError as e:
        print("SBFAIL" + json.dumps(dict(passed=False, error=str(e))))
    except Exception as e:
        print("SBFAIL" + json.dumps(dict(passed=False, error=str(e)[:200])))
_run()
"""


def run_in_sandbox(function_code, test_code, timeout=5, test_name="test_algorithm"):
    import re as _re
    test_code = _re.sub(r'from\s+main\s+import.*', '', test_code)
    test_code = _re.sub(r'from\s+.*\s+import\s+.*', '', test_code)
    import re as _rs
    # Auto-detect test function name
    tn = test_name
    for _rl in test_code.split(chr(10)):
        if _rl.strip().startswith("def test_"):
            tn = _rl.strip()[4:].split("(")[0].strip()
            break
    # Strip imports referencing external modules
    test_code = _rs.sub(r"from\s+main\s+import.*", "", test_code)
    test_code = _rs.sub(r"^import\s+.*", "", test_code, flags=_rs.MULTILINE)
    sb = _TEMPLATE.format(function_code=function_code, test_code=test_code, test_name=tn)
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "t.py")
        with open(p, "w", encoding="utf-8") as f: f.write(sb)
        start = time.time()
        try:
            r = subprocess.run(["python", p], capture_output=True, text=True, timeout=timeout, cwd=td, env=dict())
            el = round(time.time() - start, 3)
            for line in (r.stdout or "").split(chr(10)):
                if line.startswith("SBOK"):
                    return {"passed": True, "output": "", "error": "", "elapsed": el}
                if line.startswith("SBFAIL"):
                    return {"passed": False, "output": "", "error": line[6:][:300], "elapsed": el}
            return {"passed": False, "output": (r.stdout or "")[:200], "error": (r.stderr or "")[:200], "elapsed": el}
        except subprocess.TimeoutExpired:
            return {"passed": False, "output": "", "error": "Timeout " + str(timeout) + "s", "elapsed": float(timeout)}
        except Exception as e:
            return {"passed": False, "output": "", "error": str(e)[:200], "elapsed": round(time.time() - start, 3)}
