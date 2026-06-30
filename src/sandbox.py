# Sandbox: execute generated code in isolated subprocess.
# [FROZEN v1.1.0] — stable, tested, do not modify.
import os
import re
import subprocess
import tempfile
import time


# Template kept as a plain triple-quoted string (not chr()-obfuscated) so it
# is statically inspectable.  Imported inside the template's globals are
# restricted to stdlib — the test only sees what we inject.
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


def _sanitize_test_code(test_code: str) -> str:
    """Strip ``from X import Y`` and ``import X`` statements from the test.

    The sandbox only sees the freshly defined function plus a test; the test
    must not pull in unrelated modules.  We remove import lines conservatively
    (only at line start) so this does not break strings or comments.
    """
    cleaned_lines = []
    for line in test_code.splitlines():
        stripped = line.lstrip()
        if re.match(r"^from\s+\S+\s+import\s+", stripped):
            continue
        if re.match(r"^import\s+\S+", stripped):
            continue
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines)


def _resolve_python_executable() -> str:
    """Return an absolute path to the current Python interpreter.

    We deliberately do not rely on the subprocess inheriting ``PATH`` (the
    sandbox strips most env vars below), and we do not use the bare
    ``"python"`` token because that is not portable to Linux/macOS sandboxes.
    """
    return sys.executable if "sys" in dir() else "python"


# Late import to keep module import cheap and to avoid breaking the test
# fixture that monkey-patches ``sandbox.run_in_sandbox``.
import sys  # noqa: E402


def run_in_sandbox(function_code, test_code, timeout=5, test_name="test_algorithm"):
    test_code = _sanitize_test_code(test_code)

    # Auto-detect test function name when caller did not provide one.
    if test_name == "test_algorithm":
        for line in test_code.splitlines():
            stripped = line.strip()
            if stripped.startswith("def test_"):
                test_name = stripped[4:].split("(")[0].strip()
                break

    sb = _TEMPLATE.format(
        function_code=function_code,
        test_code=test_code,
        test_name=test_name,
    )

    python = sys.executable  # absolute path → no PATH lookup needed

    # Minimal but real env: keep PATH, HOME, TMPDIR/TMP so the interpreter
    # can locate stdlib and load site-packages.  Everything else (LLM keys,
    # proxy creds, etc.) is scrubbed.
    safe_env = {
        "PATH": os.environ.get("PATH", ""),
        "HOME": os.environ.get("HOME", ""),
        "USERPROFILE": os.environ.get("USERPROFILE", ""),
        "TMPDIR": os.environ.get("TMPDIR", ""),
        "TEMP": os.environ.get("TEMP", ""),
        "TMP": os.environ.get("TMP", ""),
        "SYSTEMROOT": os.environ.get("SYSTEMROOT", ""),
        "LANG": os.environ.get("LANG", "C.UTF-8"),
    }
    # On Windows, PATHEXT helps .exe resolution; on POSIX it's harmless.
    if "PATHEXT" in os.environ:
        safe_env["PATHEXT"] = os.environ["PATHEXT"]

    with tempfile.TemporaryDirectory() as td:
        script_path = os.path.join(td, "t.py")
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(sb)
        start = time.time()
        try:
            r = subprocess.run(
                [python, script_path],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=td,
                env=safe_env,
            )
            elapsed = round(time.time() - start, 3)
            for line in (r.stdout or "").splitlines():
                if line.startswith("SBOK"):
                    return {"passed": True, "output": "", "error": "", "elapsed": elapsed}
                if line.startswith("SBFAIL"):
                    return {
                        "passed": False,
                        "output": "",
                        "error": line[6:][:300],
                        "elapsed": elapsed,
                    }
            return {
                "passed": False,
                "output": (r.stdout or "")[:200],
                "error": (r.stderr or "")[:200],
                "elapsed": elapsed,
            }
        except subprocess.TimeoutExpired:
            return {
                "passed": False,
                "output": "",
                "error": "Timeout " + str(timeout) + "s",
                "elapsed": float(timeout),
            }
        except Exception as e:
            return {
                "passed": False,
                "output": "",
                "error": str(e)[:200],
                "elapsed": round(time.time() - start, 3),
            }
