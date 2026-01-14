"""Unit tests for chatbot module."""

from unittest.mock import Mock, patch

import pytest

from developing_agentic_ai.chatbot import (
    Chatbot,
    _call_llm_with_tracing,
    chat_with_tools,
    extract_provider_from_model,
    update_opik_span_and_trace_with_usage,
)


class TestExtractProviderFromModel:
    """Tests for extract_provider_from_model function."""

    def test_provider_prefix_openai(self):
        """Test extracting OpenAI provider from model string."""
        provider, model = extract_provider_from_model("openai/gpt-4")
        assert provider == "openai"
        assert model == "gpt-4"

    def test_provider_prefix_anthropic(self):
        """Test extracting Anthropic provider from model string."""
        provider, model = extract_provider_from_model("anthropic/claude-3-opus")
        assert provider == "anthropic"
        assert model == "claude-3-opus"

    def test_provider_prefix_google(self):
        """Test extracting Google provider from model string."""
        provider, model = extract_provider_from_model("google/gemini-pro")
        assert provider == "google"
        assert model == "gemini-pro"

    def test_provider_prefix_with_spaces(self):
        """Test extracting provider when model string has spaces."""
        provider, model = extract_provider_from_model("openai / gpt-4")
        assert provider == "openai"
        assert model == "gpt-4"

    def test_unknown_provider_prefix(self):
        """Test with unknown provider prefix returns None."""
        provider, model = extract_provider_from_model("unknown/model-name")
        assert provider is None
        # Unknown providers are not stripped, so the full string is returned
        assert model == "unknown/model-name"

    def test_no_provider_prefix_gpt(self):
        """Test GPT model without prefix defaults to OpenAI."""
        with patch("developing_agentic_ai.chatbot.get_llm_provider") as mock_provider:
            mock_provider.side_effect = Exception("Not found")
            provider, model = extract_provider_from_model("gpt-3.5-turbo")
            assert provider == "openai"
            assert model == "gpt-3.5-turbo"

    def test_no_provider_prefix_claude(self):
        """Test Claude model without prefix defaults to Anthropic."""
        with patch("developing_agentic_ai.chatbot.get_llm_provider") as mock_provider:
            mock_provider.side_effect = Exception("Not found")
            provider, model = extract_provider_from_model("claude-3-sonnet")
            assert provider == "anthropic"
            assert model == "claude-3-sonnet"

    def test_no_provider_prefix_gemini(self):
        """Test Gemini model without prefix defaults to Google."""
        with patch("developing_agentic_ai.chatbot.get_llm_provider") as mock_provider:
            mock_provider.side_effect = Exception("Not found")
            provider, model = extract_provider_from_model("gemini-pro")
            assert provider == "google"
            assert model == "gemini-pro"

    def test_empty_model_string(self):
        """Test with empty model string."""
        provider, model = extract_provider_from_model("")
        assert provider is None
        assert model == ""

    def test_none_model_string(self):
        """Test with None model string."""
        provider, model = extract_provider_from_model(None)
        assert provider is None
        assert model is None

    def test_litellm_provider_detection(self):
        """Test using litellm's get_llm_provider function."""
        with patch("developing_agentic_ai.chatbot.get_llm_provider") as mock_provider:
            mock_provider.return_value = (None, "openai", None)
            provider, model = extract_provider_from_model("gpt-4")
            assert provider == "openai"
            assert model == "gpt-4"

    def test_lowercase_provider_normalization(self):
        """Test that provider names are normalized to lowercase."""
        provider, model = extract_provider_from_model("OPENAI/GPT-4")
        assert provider == "openai"
        assert model == "GPT-4"


class TestUpdateOpikSpanAndTraceWithUsage:
    """Tests for update_opik_span_and_trace_with_usage function."""

    @patch("developing_agentic_ai.chatbot.opik_context")
    def test_update_with_usage(self, mock_opik_context):
        """Test updating span and trace with usage information."""
        # Mock response with usage
        mock_resp = Mock()
        mock_resp.usage = Mock()
        mock_resp.usage.prompt_tokens = 10
        mock_resp.usage.completion_tokens = 20
        mock_resp.usage.total_tokens = 30

        # Mock trace data
        mock_opik_context.get_current_trace_data.return_value = {"metadata": {}}

        update_opik_span_and_trace_with_usage("openai/gpt-4", mock_resp)

        # Verify span was updated
        mock_opik_context.update_current_span.assert_called_once()
        call_kwargs = mock_opik_context.update_current_span.call_args[1]
        assert call_kwargs["model"] == "gpt-4"
        assert call_kwargs["provider"] == "openai"
        assert call_kwargs["usage"]["prompt_tokens"] == 10
        assert call_kwargs["usage"]["completion_tokens"] == 20
        assert call_kwargs["usage"]["total_tokens"] == 30

    @patch("developing_agentic_ai.chatbot.opik_context")
    def test_update_without_usage(self, mock_opik_context):
        """Test updating span when response has no usage information."""
        mock_resp = Mock()
        mock_resp.usage = None

        update_opik_span_and_trace_with_usage("openai/gpt-4", mock_resp)

        # Should not update span if no usage
        mock_opik_context.update_current_span.assert_not_called()

    @patch("developing_agentic_ai.chatbot.opik_context")
    def test_update_with_partial_usage(self, mock_opik_context):
        """Test updating span with partial usage information."""
        mock_resp = Mock()
        mock_resp.usage = Mock()
        mock_resp.usage.prompt_tokens = 10
        mock_resp.usage.completion_tokens = None
        mock_resp.usage.total_tokens = None

        mock_opik_context.get_current_trace_data.return_value = {"metadata": {}}

        update_opik_span_and_trace_with_usage("anthropic/claude-3", mock_resp)

        call_kwargs = mock_opik_context.update_current_span.call_args[1]
        assert call_kwargs["usage"]["prompt_tokens"] == 10
        assert "completion_tokens" not in call_kwargs["usage"]
        assert "total_tokens" not in call_kwargs["usage"]

    @patch("developing_agentic_ai.chatbot.opik_context")
    def test_update_trace_metadata(self, mock_opik_context):
        """Test that trace metadata is updated with provider and model."""
        mock_resp = Mock()
        mock_resp.usage = Mock()
        mock_resp.usage.prompt_tokens = 10
        mock_resp.usage.completion_tokens = 20
        mock_resp.usage.total_tokens = 30

        mock_opik_context.get_current_trace_data.return_value = {"metadata": {}}

        update_opik_span_and_trace_with_usage("google/gemini-pro", mock_resp)

        # Verify trace was updated
        mock_opik_context.update_current_trace.assert_called_once()
        call_kwargs = mock_opik_context.update_current_trace.call_args[1]
        assert call_kwargs["metadata"]["provider"] == "google"
        assert call_kwargs["metadata"]["model"] == "gemini-pro"

    @patch("developing_agentic_ai.chatbot.opik_context")
    def test_exception_handling(self, mock_opik_context):
        """Test that exceptions are handled gracefully."""
        mock_resp = Mock()
        mock_resp.usage = Mock()
        mock_resp.usage.prompt_tokens = 10

        # Make opik_context methods raise exceptions
        mock_opik_context.update_current_span.side_effect = Exception("Error")
        mock_opik_context.get_current_trace_data.side_effect = Exception("Error")

        # Should not raise exception
        update_opik_span_and_trace_with_usage("openai/gpt-4", mock_resp)


class TestCallLLMWithTracing:
    """Tests for _call_llm_with_tracing function."""

    @patch("developing_agentic_ai.chatbot.litellm")
    @patch("developing_agentic_ai.chatbot.update_opik_span_and_trace_with_usage")
    def test_call_llm_success(self, mock_update_usage, mock_litellm):
        """Test successful LLM call."""
        # Mock response
        mock_resp = Mock()
        mock_resp.choices = [Mock()]
        mock_resp.choices[0].message = Mock()
        mock_litellm.completion.return_value = mock_resp

        messages = [{"role": "user", "content": "Hello"}]
        result = _call_llm_with_tracing("gpt-4", messages)

        assert result == mock_resp
        mock_litellm.completion.assert_called_once()
        mock_update_usage.assert_called_once_with("gpt-4", mock_resp)

    @patch("developing_agentic_ai.chatbot.litellm")
    @patch("developing_agentic_ai.chatbot.update_opik_span_and_trace_with_usage")
    def test_call_llm_with_tools(self, mock_update_usage, mock_litellm):
        """Test LLM call with tools."""
        mock_resp = Mock()
        mock_resp.choices = [Mock()]
        mock_resp.choices[0].message = Mock()
        mock_litellm.completion.return_value = mock_resp

        messages = [{"role": "user", "content": "Hello"}]
        tools = [{"type": "function", "function": {"name": "test_tool"}}]

        _call_llm_with_tracing("gpt-4", messages, tools=tools)

        call_kwargs = mock_litellm.completion.call_args[1]
        assert "tools" in call_kwargs
        assert call_kwargs["tool_choice"] == "auto"

    @patch("developing_agentic_ai.chatbot.litellm")
    def test_call_llm_none_response(self, mock_litellm):
        """Test handling of None response from LLM."""
        mock_litellm.completion.return_value = None

        with pytest.raises(ValueError, match="LLM returned None response"):
            _call_llm_with_tracing("gpt-4", [])

    @patch("developing_agentic_ai.chatbot.litellm")
    def test_call_llm_missing_choices(self, mock_litellm):
        """Test handling of response missing choices attribute."""
        mock_resp = Mock()
        del mock_resp.choices
        mock_litellm.completion.return_value = mock_resp

        with pytest.raises(ValueError, match="LLM response missing 'choices' attribute"):
            _call_llm_with_tracing("gpt-4", [])


class TestChatWithTools:
    """Tests for chat_with_tools function."""

    @patch("developing_agentic_ai.chatbot._call_llm_with_tracing")
    @patch("developing_agentic_ai.chatbot.opik_context")
    @patch("developing_agentic_ai.chatbot.track")
    @patch("developing_agentic_ai.chatbot.pretty_print")
    def test_chat_without_tools(
        self, mock_pretty_print, mock_track, mock_opik_context, mock_call_llm
    ):
        """Test chat without tool calls."""
        # Mock LLM response without tool calls
        mock_resp = Mock()
        mock_message = Mock()
        mock_message.content = "Hello, how can I help?"
        mock_message.tool_calls = None
        mock_resp.choices = [Mock()]
        mock_resp.choices[0].message = mock_message
        mock_call_llm.return_value = mock_resp

        # Mock track decorator
        mock_track.side_effect = lambda name=None, type=None: lambda f: f

        messages = [{"role": "system", "content": "You are a helpful assistant."}]
        tools = {}

        result = chat_with_tools("Hello", "gpt-4", messages, tools, thread_id="test-thread")

        assert result == "Hello, how can I help?"
        # Messages: system, user, assistant (from loop), assistant (final)
        assert len(messages) == 4
        mock_pretty_print.assert_called_once()

    @patch("developing_agentic_ai.chatbot._call_llm_with_tracing")
    @patch("developing_agentic_ai.chatbot.opik_context")
    @patch("developing_agentic_ai.chatbot.track")
    @patch("developing_agentic_ai.chatbot.pretty_print")
    def test_chat_with_tool_calls(
        self, mock_pretty_print, mock_track, mock_opik_context, mock_call_llm
    ):
        """Test chat with tool calls."""

        # Mock tool function
        def mock_tool_func(city: str) -> str:
            return f"Weather in {city}: Sunny"

        # Mock LLM response with tool calls
        mock_resp = Mock()
        mock_message = Mock()
        mock_tool_call = Mock()
        mock_tool_call.id = "call_123"
        mock_tool_call.function = Mock()
        mock_tool_call.function.name = "get_weather"
        mock_tool_call.function.arguments = '{"city": "Boston"}'
        mock_message.content = None
        mock_message.tool_calls = [mock_tool_call]
        mock_resp.choices = [Mock()]
        mock_resp.choices[0].message = mock_message
        mock_call_llm.return_value = mock_resp

        # Second call (after tool execution) returns final response
        mock_resp2 = Mock()
        mock_message2 = Mock()
        mock_message2.content = "The weather is sunny."
        mock_message2.tool_calls = None
        mock_resp2.choices = [Mock()]
        mock_resp2.choices[0].message = mock_message2
        mock_call_llm.side_effect = [mock_resp, mock_resp2]

        # Mock track decorator
        mock_track.side_effect = lambda name=None, type=None: lambda f: f

        messages = [{"role": "system", "content": "You are a helpful assistant."}]
        tools = {"get_weather": mock_tool_func}

        result = chat_with_tools("What's the weather?", "gpt-4", messages, tools)

        assert result == "The weather is sunny."
        assert mock_call_llm.call_count == 2
        # Verify tool result was added to messages
        assert any(msg.get("role") == "tool" for msg in messages)

    @patch("developing_agentic_ai.chatbot._call_llm_with_tracing")
    @patch("developing_agentic_ai.chatbot.opik_context")
    @patch("developing_agentic_ai.chatbot.track")
    def test_chat_with_thread_id(self, mock_track, mock_opik_context, mock_call_llm):
        """Test chat with thread_id updates trace context."""
        mock_resp = Mock()
        mock_message = Mock()
        mock_message.content = "Response"
        mock_message.tool_calls = None
        mock_resp.choices = [Mock()]
        mock_resp.choices[0].message = mock_message
        mock_call_llm.return_value = mock_resp

        mock_track.side_effect = lambda name=None, type=None: lambda f: f

        messages = [{"role": "system", "content": "You are a helpful assistant."}]
        tools = {}

        chat_with_tools("Hello", "gpt-4", messages, tools, thread_id="test-thread-123")

        mock_opik_context.update_current_trace.assert_called_once_with(thread_id="test-thread-123")


class TestChatbot:
    """Tests for Chatbot class."""

    def test_init(self):
        """Test Chatbot initialization."""
        chatbot = Chatbot("gpt-4", "You are helpful", [])
        assert chatbot.model == "gpt-4"
        assert chatbot.system_prompt == "You are helpful"
        assert chatbot.tools == []
        assert isinstance(chatbot.thread_id, str)
        assert len(chatbot.messages) == 1
        assert chatbot.messages[0]["role"] == "system"
        assert chatbot.messages[0]["content"] == "You are helpful"

    def test_init_defaults(self):
        """Test Chatbot initialization with defaults."""
        chatbot = Chatbot("gpt-4")
        assert chatbot.model == "gpt-4"
        assert chatbot.system_prompt == "Please answer the question"
        assert chatbot.tools == []
        assert len(chatbot.messages) == 1

    def test_init_with_tools(self):
        """Test Chatbot initialization with tools."""
        tools = [{"name": "test_tool"}]
        chatbot = Chatbot("gpt-4", tools=tools)
        assert chatbot.tools == tools

    def test_clear_messages(self):
        """Test clearing message history."""
        chatbot = Chatbot("gpt-4", "System prompt")
        chatbot.messages.append({"role": "user", "content": "Hello"})
        chatbot.messages.append({"role": "assistant", "content": "Hi"})

        chatbot.clear_messages()

        assert len(chatbot.messages) == 1
        assert chatbot.messages[0]["role"] == "system"
        assert chatbot.messages[0]["content"] == "System prompt"

    @patch("developing_agentic_ai.chatbot.chat_with_tools")
    def test_chat(self, mock_chat_with_tools):
        """Test chat method."""
        mock_chat_with_tools.return_value = "Response"

        chatbot = Chatbot("gpt-4")
        result = chatbot.chat("Hello")

        assert result == "Response"
        mock_chat_with_tools.assert_called_once()
        call_kwargs = mock_chat_with_tools.call_args[1]
        assert call_kwargs["user_text"] == "Hello"
        assert call_kwargs["model"] == "gpt-4"
        assert call_kwargs["thread_id"] == chatbot.thread_id

    @patch("builtins.input")
    def test_get_user_input(self, mock_input):
        """Test get_user_input method."""
        mock_input.return_value = "Hello"

        chatbot = Chatbot("gpt-4")
        result = chatbot.get_user_input()

        assert result == "Hello"
        mock_input.assert_called_once_with(">>> ")

    @patch("builtins.input")
    def test_get_user_input_eof(self, mock_input):
        """Test get_user_input handles EOFError."""
        mock_input.side_effect = EOFError()

        chatbot = Chatbot("gpt-4")
        result = chatbot.get_user_input()

        assert result == "exit"

    @patch("developing_agentic_ai.chatbot.Chatbot.get_user_input")
    @patch("developing_agentic_ai.chatbot.Chatbot.chat")
    def test_start(self, mock_chat, mock_get_input):
        """Test start method runs interactive loop."""
        mock_get_input.side_effect = ["Hello", "How are you?", "exit"]

        chatbot = Chatbot("gpt-4")
        chatbot.start()

        assert mock_chat.call_count == 2
        assert mock_chat.call_args_list[0][0][0] == "Hello"
        assert mock_chat.call_args_list[1][0][0] == "How are you?"
