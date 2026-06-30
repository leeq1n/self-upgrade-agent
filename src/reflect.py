"""Reflection loop: analyze test failures and improve generated code."""
import json
import logging
from src.llm import chat_simple, LLMConfig
from src.sandbox import run_in_sandbox

logger = logging.getLogger(__name__)


def reflect_and_improve(function_code, test_code, error_msg, llm_config=None, max_attempts=3):
    """LLM analyzes test failure and rewrites the code.

    Returns:
        {"fixed": True/False, "code": str, "attempts": int, "errors": [str]}
    """
    errors = [error_msg]
    current_code = function_code

    for attempt in range(max_attempts):
        prompt = (
            f"A Python test failed. Fix the code to pass the test.\n\n"
            f"ORIGINAL CODE:\n{current_code}\n\n"
            f"TEST:\n{test_code}\n\n"
            f"ERROR:\n{errors[-1]}\n\n"
            f"Write ONLY the corrected function, nothing else. "
            f"Just the function body, no extra text."
        )

        fixed_code = chat_simple(prompt, config=llm_config)
        if not fixed_code:
            errors.append("LLM returned empty response")
            continue

        result = run_in_sandbox(fixed_code, test_code, timeout=5)
        if result.get("passed"):
            return {"fixed": True, "code": fixed_code, "attempts": attempt + 1, "errors": errors}

        new_error = result.get("error", "unknown")
        if new_error and new_error not in errors:
            errors.append(new_error)
        else:
            errors.append(f"Attempt {attempt + 2} failed: {new_error[:100]}")

    return {"fixed": False, "code": current_code, "attempts": max_attempts, "errors": errors}
