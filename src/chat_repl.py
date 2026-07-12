"""Interactive chat subcommand (per 你 vision '其他agent产品').

Per user 2026-07-11 '好, 继续推进' + 自上而下/分治 + LITERATURE:

Per 你 vision 2026-07-08 + '像其他agent产品一样':
- Real interactive chat (multi-turn)
- REPL with history persistence (per P19)
- Per LITERATURE Signal-to-Fix: minimal, 奥卡姆

Per 自上而下/分治 (user meta-principle):
- Big: project as 'real agent product' (interactive chat)
- Sub-task 1 (this commit): chat REPL with history
- Sub-task 2 (future): streaming responses
- Sub-task 3 (future): tool use during chat

Per P23 doc-first: spec exists (README line 109: 'python -m self_upgrade run').
This extends with multi-turn chat.
Per P18: regression tests required.
"""
import json
import datetime
from pathlib import Path
from typing import Optional, List, Dict


DEFAULT_HISTORY = Path("chat_history.json")


def load_history(path=None) -> List[Dict]:
    """Load chat history from JSONL file.

    Per P19: persistence for cross-session memory.
    Returns: list of {role, content, timestamp} dicts.
    """
    if path is None:
        path = DEFAULT_HISTORY
    path = Path(path)
    if not path.exists():
        return []
    history = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                history.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return history


def save_message(message, path=None):
    """Append a single message to chat history.

    Per LITERATURE: append-only persistence.
    """
    if path is None:
        path = DEFAULT_HISTORY
    path = Path(path)
    # Ensure timestamp
    if "timestamp" not in message:
        message["timestamp"] = datetime.datetime.now().isoformat()
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(message, ensure_ascii=False) + "\n")


def build_messages_prompt(history, user_input, system="You are a helpful assistant."):
    """Build messages list for LLM chat call.

    Per LITERATURE: combine history + new user input.
    Returns: list of {role, content} dicts.
    """
    messages = [{"role": "system", "content": system}]
    for msg in history:
        if msg.get("role") in ("user", "assistant") and msg.get("content"):
            messages.append({
                "role": msg["role"],
                "content": msg["content"],
            })
    messages.append({"role": "user", "content": user_input})
    return messages


def format_chat_response(response_text):
    """Format chat response for CLI display.

    Per LITERATURE: human-readable output.
    """
    return f"\n[assistant]\n{response_text}\n"


def chat_repl(llm_call=None, history_path=None, system=None, max_history=50):
    """Interactive REPL with history persistence.

    Per 你 vision: real agent product.
    Per P19: cross-session memory via history file.
    Per LITERATURE: minimal, 奥卡姆.

    Args:
        llm_call: callable(messages) -> response_text (for testing)
                  If None, uses real LLM
        history_path: optional chat_history.json path
        system: optional system prompt
        max_history: max history turns to keep in context (default 50)
    """
    if history_path is None:
        history_path = DEFAULT_HISTORY
    if system is None:
        system = "You are a helpful assistant."
    history = load_history(history_path)
    if llm_call is None:
        # Real LLM call
        from src.llm import LLMConfig
        try:
            config = LLMConfig.from_env()
            llm_call = lambda messages: _real_llm_call(messages, config)
        except Exception as e:
            print(f"[error] LLM config failed: {e}")
            return {"turns": 0}
    print("=" * 60)
    print("Self-Upgrade Agent - Interactive Chat")
    print("Per 你 vision: real agent product")
    print("Type 'exit', 'quit', or Ctrl-C to leave.")
    print("=" * 60)
    turns = 0
    try:
        while True:
            try:
                user_input = input("\n[you] ").strip()
            except EOFError:
                break
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", ":q"):
                break
            # Save user message
            save_message({"role": "user", "content": user_input},
                         path=history_path)
            # Build messages + call LLM
            messages = build_messages_prompt(history, user_input,
                                              system=system)
            try:
                response_text = llm_call(messages)
            except Exception as e:
                print(f"[error] LLM call failed: {e}")
                continue
            # Save assistant response
            save_message({"role": "assistant", "content": response_text},
                         path=history_path)
            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": response_text})
            # Trim history (keep last max_history messages)
            if len(history) > max_history:
                history = history[-max_history:]
            # Display
            print(format_chat_response(response_text))
            turns += 1
    except KeyboardInterrupt:
        print("\n[stopped by user]")
    return {"turns": turns}


def _real_llm_call(messages, config):
    """Real LLM call using config.

    Per LITERATURE: real LLM integration.
    """
    from src.llm import chat
    response = chat(messages, config=config)
    if hasattr(response, "content"):
        return response.content
    return str(response)


def main():
    """CLI: start interactive chat REPL."""
    return chat_repl() or 0


if __name__ == "__main__":
    import sys
    sys.exit(main())