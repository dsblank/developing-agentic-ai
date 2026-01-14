import json
import os
import uuid
from typing import Optional, Tuple

import litellm
from litellm.utils import get_llm_provider
from opik import opik_context, track

from .utils import (
    create_function_definition,
    pretty_print,
)

PROJECT_NAME = os.environ.get("OPIK_PROJECT_NAME")
if PROJECT_NAME is None:
    PROJECT_NAME = os.environ["OPIK_PROJECT_NAME"] = "chatbot-session"


def extract_provider_from_model(model: str) -> Tuple[Optional[str], str]:
    """
    Extract provider name from model string and return normalized model name.

    Handles formats like:
    - "openai/gpt-5-nano" -> ("openai", "gpt-5-nano")
    - "gpt-3.5-turbo" -> (None or provider from litellm, "gpt-3.5-turbo")
    - "anthropic/claude-3-opus" -> ("anthropic", "claude-3-opus")

    Args:
        model: Model string that may contain provider prefix

    Returns:
        Tuple of (provider_name, normalized_model_name)
    """
    if not model:
        return None, model

    # Check if model string has provider prefix (format: "provider/model-name")
    if "/" in model:
        provider_part, model_part = model.split("/", 1)
        provider_part = provider_part.strip()
        model_part = model_part.strip()
        # Common provider names (normalize to lowercase)
        provider_lower = provider_part.lower()
        known_providers = {
            "openai",
            "anthropic",
            "google",
            "cohere",
            "mistral",
            "azure",
            "bedrock",
            "vertex",
            "together",
            "replicate",
            "huggingface",
            "ollama",
            "groq",
            "deepinfra",
            "anyscale",
            "perplexity",
            "voyage",
            "nvidia",
            "cloudflare",
            "cerebras",
            "predibase",
        }
        if provider_lower in known_providers:
            return provider_lower, model_part

    # Try using litellm's get_llm_provider function
    provider = None
    try:
        _, provider, _ = get_llm_provider(model=model)
        if provider:
            provider = provider.lower() if isinstance(provider, str) else None
    except Exception:
        pass

    # Fallback: Map common model names to providers
    if not provider:
        model_lower = model.lower()
        if model_lower.startswith("gpt") or "gpt" in model_lower:
            provider = "openai"
        elif model_lower.startswith("claude") or "claude" in model_lower:
            provider = "anthropic"
        elif model_lower.startswith("gemini") or "gemini" in model_lower:
            provider = "google"
        elif model_lower.startswith("llama") or "llama" in model_lower:
            # Llama models could be from various providers, but default to meta if unsure
            pass  # Keep as None since provider is unclear

    return provider, model


def update_opik_span_and_trace_with_usage(model: str, resp) -> None:
    """
    Extract token counts and usage information from LLM response and update Opik span and trace.

    This function:
    1. Extracts provider and normalizes model name
    2. Extracts token counts (prompt_tokens, completion_tokens, total_tokens) from response
    3. Updates the current span with provider, model, and usage
    4. Updates trace metadata with provider and model (usage is aggregated by Opik)

    Args:
        model: Model string (may contain provider prefix like "openai/gpt-5-nano")
        resp: LLM response object from litellm.completion()
    """
    try:
        # Extract provider from model string (with fallback parsing) and normalize model name
        provider, normalized_model = extract_provider_from_model(model)

        # Extract token counts from response
        usage_dict = {}
        if hasattr(resp, "usage") and resp.usage:
            prompt_tokens = getattr(resp.usage, "prompt_tokens", None)
            completion_tokens = getattr(resp.usage, "completion_tokens", None)
            total_tokens = getattr(resp.usage, "total_tokens", None)

            if prompt_tokens is not None:
                usage_dict["prompt_tokens"] = prompt_tokens
            if completion_tokens is not None:
                usage_dict["completion_tokens"] = completion_tokens
            if total_tokens is not None:
                usage_dict["total_tokens"] = total_tokens

        # Update span with provider, model, and usage information
        # Always include provider if available, and always include usage if present
        if usage_dict:
            update_kwargs = {
                "model": normalized_model,  # Use normalized model (without provider prefix)
                "usage": usage_dict,
            }
            # Always set provider if we could determine it (required for cost estimation)
            if provider:
                update_kwargs["provider"] = provider

            try:
                opik_context.update_current_span(**update_kwargs)

                # Also update trace metadata with provider and model for cost estimation
                # Note: Usage is aggregated automatically by Opik from spans, we just need provider/model
                try:
                    # Get existing metadata from trace data - always fetch fresh to avoid overwriting
                    existing_metadata = {}
                    try:
                        trace_data = opik_context.get_current_trace_data()

                        # Handle TraceData object (not just dict)
                        if trace_data:
                            # Check if it's a dict
                            if isinstance(trace_data, dict):
                                metadata = trace_data.get("metadata")
                                if isinstance(metadata, dict):
                                    existing_metadata = metadata.copy()
                                else:
                                    existing_metadata = {}
                            # Check if it's a TraceData object with metadata attribute
                            elif hasattr(trace_data, "metadata"):
                                metadata = getattr(trace_data, "metadata", None)
                                if isinstance(metadata, dict):
                                    existing_metadata = metadata.copy()
                                else:
                                    existing_metadata = {}
                    except Exception:
                        existing_metadata = {}

                    # Add provider and model to metadata if available (preserve existing metadata)
                    if provider:
                        existing_metadata["provider"] = provider
                    if normalized_model:
                        existing_metadata["model"] = normalized_model

                    # Update trace metadata with provider and model
                    # Usage will be aggregated automatically by Opik from spans
                    if provider or normalized_model:
                        opik_context.update_current_trace(metadata=existing_metadata)
                except Exception:
                    pass
            except Exception:
                pass
    except Exception:
        pass


@track(name="llm_completion", type="llm")
def _call_llm_with_tracing(model, messages, tools=None, **kwargs):
    """Call LLM with proper Opik span management within the current trace.

    Uses @track decorator to ensure it creates a span within the existing trace.
    """
    try:
        # Call the LLM - Opik will automatically track this as a span within the current trace
        call_kwargs = kwargs.copy()
        if tools:
            call_kwargs.update({"tools": tools, "tool_choice": "auto"})

        resp = litellm.completion(
            model=model,
            messages=messages,
            **call_kwargs,
        )

        if resp is None:
            raise ValueError("LLM returned None response")

        if not hasattr(resp, "choices"):
            raise ValueError(f"LLM response missing 'choices' attribute: {resp}")

        # Extract token counts and update span with usage information
        update_opik_span_and_trace_with_usage(model, resp)

        return resp

    except Exception:
        raise


@track
def chat_with_tools(user_text: str, model: str, messages: list, tools: list, thread_id: str = None):
    """Chat function that handles LLM calls with tool execution."""
    # Update trace context with thread_id if provided (like reference does)
    if thread_id:
        try:
            context_updates = {"thread_id": thread_id}
            opik_context.update_current_trace(**context_updates)
        except Exception:
            pass

    # Add user message to persistent history (like reference does)
    user_msg = {"role": "user", "content": user_text}
    messages.append(user_msg)

    # Tool loop with tool calling using persistent messages
    tools_dict = {
        key: track(name=value.__name__, type="tool")(value) for key, value in tools.items()
    }
    tool_defs = [create_function_definition(function) for function in tools_dict.values()]

    while True:
        response = _call_llm_with_tracing(model=model, messages=messages, tools=tool_defs)
        msg = response.choices[0].message

        # Manually construct the assistant message to ensure tool_calls are preserved
        assistant_msg = {"role": "assistant", "content": msg.content if msg.content else None}

        # Add tool_calls if they exist
        if msg.tool_calls:
            assistant_msg["tool_calls"] = [
                {
                    "id": tool_call.id,
                    "type": "function",
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments,
                    },
                }
                for tool_call in msg.tool_calls
            ]

        messages.append(assistant_msg)

        if msg.tool_calls:
            for tool_call in msg.tool_calls:
                tool_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                tool_func = tools_dict.get(tool_name)
                tool_result = tool_func(**arguments) if tool_func else "Unknown tool"

                # Ensure tool_result is a string
                if not isinstance(tool_result, str):
                    tool_result = json.dumps(tool_result)

                messages.append(
                    {"role": "tool", "tool_call_id": tool_call.id, "content": tool_result}
                )
        else:
            pretty_print(msg.content)
            # Return the final assistant response (strip whitespace like reference)
            text_reply = (msg.content or "").strip()
            # Add assistant's final response to persistent history
            messages.append({"role": "assistant", "content": text_reply})
            return text_reply


class Chatbot:
    def __init__(
        self, model: str, system_prompt: str = "Please answer the question", tools: list = None
    ):
        """Initialize chatbot with model, system prompt, and tools."""
        self.model = model
        self.system_prompt = system_prompt
        self.tools = tools if tools is not None else []
        # Generate unique thread-id for this chatbot instance
        self.thread_id = str(uuid.uuid4())
        self.clear_messages()

    def get_user_input(self, prompt: str = ">>> ") -> str:
        """
        Ask the user for input
        """
        try:
            user_text = input(">>> ")
        except EOFError:
            user_text = "exit"
        return user_text

    def start(self):
        """Start the interactive chat loop."""
        user_text = self.get_user_input()
        while user_text != "exit":
            self.chat(user_text)
            user_text = self.get_user_input()
        print("")

    @track
    def chat(self, user_text: str) -> str:
        """Chat method that creates a trace and delegates to chat_with_tools."""
        return chat_with_tools(
            user_text=user_text,
            model=self.model,
            messages=self.messages,
            tools=self.tools,
            thread_id=self.thread_id,
        )

    def clear_messages(self) -> None:
        """Clear the message history, keeping only the system prompt."""
        self.messages = [
            {
                "role": "system",
                "content": self.system_prompt,
            }
        ]
