"""Tests for streaming chat (per 你 vision 'real agent product' sub-task 2).

Per 自上而下/分治:
- Big: project as 'real agent product'
- Sub-task 1 (done): chat REPL
- Sub-task 2 (this): streaming responses

Per P18: regression tests required.
"""
from unittest.mock import patch, MagicMock

from src.chat_repl import stream_response, chat_repl_streaming


class TestStreamResponse:
    """Test per-token streaming (per LITERATURE 奥卡姆)."""

    def test_stream_emits_tokens(self):
        """stream_response: on_token called for each word."""
        def fake_llm(messages):
            return "Hello world from streaming"
        tokens = []
        def on_token(t):
            tokens.append(t)
        result = stream_response.__wrapped__ if hasattr(stream_response, "__wrapped__") else stream_response
        # Use mocked config
        mock_config = MagicMock()
        with patch("src.chat_repl._real_llm_call", return_value="Hello world"):
            response = stream_response([{"role": "user", "content": "hi"}],
                                         on_token=on_token,
                                         config=mock_config)
        # "Hello world" = 2 words = 2 tokens ("Hello", " world")
        assert len(tokens) == 2
        assert tokens[0] == "Hello"
        assert tokens[1] == " world"
        assert response == "Hello world"

    def test_stream_no_callback(self):
        """stream_response: works without on_token."""
        mock_config = MagicMock()
        with patch("src.chat_repl._real_llm_call", return_value="Response"):
            response = stream_response([{"role": "user", "content": "hi"}],
                                         on_token=None, config=mock_config)
        assert response == "Response"


class TestChatReplStreaming:
    """Test streaming REPL (per sub-task 2)."""

    def test_streaming_repl_multi_turn(self, tmp_path):
        """chat_repl_streaming: multi-turn with streaming display."""
        path = tmp_path / "history.jsonl"
        responses = iter(["first response here", "second response there"])
        def fake_llm(messages):
            return next(responses)
        with patch("builtins.input", side_effect=["hi", "next?", "exit"]):
            result = chat_repl_streaming(llm_call=fake_llm,
                                          history_path=path)
        assert result["turns"] == 2
        # History saved
        from src.chat_repl import load_history
        history = load_history(path)
        assert len(history) == 4  # 2 user + 2 assistant
