"""Built-in tools for the self-upgrade agent.

[FROZEN v1.1.0] — stable, tested, do not modify.
"""
__version__ = "1.1.0"
import subprocess, os, math as _math


def tool_shell(command: str) -> str:
    """Run a shell command and return output."""
    try:
        r = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
        return (r.stdout or r.stderr or "(no output)")[:500]
    except Exception as e:
        return f"Shell error: {e}"

def tool_read_file(path: str) -> str:
    """Read a file's contents."""
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()[:1000]
    except Exception as e:
        return f"Read error: {e}"

def tool_calculate(expression: str) -> str:
    """Evaluate a math expression safely."""
    try:
        allowed = {"abs": abs, "round": round, "min": min, "max": max,
                   "int": int, "float": float, "pow": pow, "sum": sum, 
                   "len": len, "sqrt": _math.sqrt, "pi": _math.pi}
        result = eval(expression, {"__builtins__": {}}, allowed)
        return str(result)
    except Exception as e:
        return f"Calc error: {e}"

def tool_write_file(path: str, content: str) -> str:
    """Write content to a file."""
    try:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Written {len(content)} bytes to {path}"
    except Exception as e:
        return f"Write error: {e}"
