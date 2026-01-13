import litellm
import opik
from opik.opik_context import get_current_span_data
from opik import track
import json

from .utils import (
    pretty_print,
    create_function_definition,
)


opik_client = opik.Opik()
project_url = opik_client.get_project_url()


@track
def chatbot(tools, messages):
    pretty_print(f"Your project is available here: [agents-from-scratch]({project_url})")
    tool_defs = [create_function_definition(tool) for tool in tools.values()]
    print("Enter 'exit' to exit chatbot")
    user_prompt = input(">>> ")
    while user_prompt not in ["exit", ""]:
        messages.append({"role": "user", "content": user_prompt})
        while True:
            # Get current span data to create child spans
            current_span_data = get_current_span_data()

            # Create a child span for the LLM call
            if current_span_data:
                # Create child span using the opik client
                llm_span = opik_client.span(
                    trace_id=current_span_data.trace_id,
                    parent_span_id=current_span_data.id,
                    name="llm_completion",
                    type="llm",
                    input={"messages": messages, "tools": tool_defs},
                    metadata={"model": MODEL, "tags": ["chatbot"]},
                )

            response = litellm.completion(
                model=MODEL,
                messages=messages,
                tools=tool_defs,
                tool_choice="auto",
            )

            # End the LLM span with the response
            if current_span_data:
                llm_span.end(
                    output={"response": response.choices[0].message.to_dict()},
                    usage=response.usage.model_dump() if response.usage else None,
                    model=MODEL,
                    provider="openai",
                )

            msg = response.choices[0].message
            messages.append(msg.to_dict())
            if msg.tool_calls:
                for tool_call in msg["tool_calls"]:
                    tool_name = tool_call["function"]["name"]
                    arguments = json.loads(tool_call["function"]["arguments"])
                    tool_func = tools.get(tool_name)

                    # Create tool span as child of LLM span
                    if current_span_data:
                        tool_span = opik_client.span(
                            trace_id=current_span_data.trace_id,
                            parent_span_id=llm_span.id,  # Child of LLM span, not chatbot span
                            name=tool_name,
                            type="tool",
                            input={"tool_name": tool_name, "arguments": arguments},
                            metadata={"tool_name": tool_name},
                        )

                    if not tool_func:
                        tool_result = "Unknown tool"
                    else:
                        tool_result = tool_func(**arguments)

                    # End the tool span
                    if current_span_data:
                        tool_span.end(
                            output={"result": tool_result}, metadata={"tool_name": tool_name}
                        )

                    messages.append(
                        {"role": "tool", "tool_call_id": tool_call["id"], "content": tool_result}
                    )
            else:
                pretty_print(msg["content"])
                break
        print()
        user_prompt = input(">>> ")
