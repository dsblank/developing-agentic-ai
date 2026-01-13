import json

import litellm
import opik
from opik import track

from .utils import (
    create_function_definition,
    pretty_print,
)


@track
def tool_loop(model, messages, tools):
    tool_defs = [create_function_definition(function) for function in tools.values()]
    while True:
        response = litellm.completion(
            model=model, messages=messages, tools=tool_defs, tool_choice="auto"
        )
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
                tool_func = tools.get(tool_name)
                tool_result = tool_func(**arguments) if tool_func else "Unknown tool"

                # Ensure tool_result is a string
                if not isinstance(tool_result, str):
                    tool_result = json.dumps(tool_result)

                messages.append(
                    {"role": "tool", "tool_call_id": tool_call.id, "content": tool_result}
                )
        else:
            pretty_print(msg.content)
            break


def chatbot(model, system_prompt="Please answer the question", tools=None):
    opik_client = opik.Opik()
    project_url = opik_client.get_project_url()

    pretty_print(f"Your project is available here: [agents-from-scratch]({project_url})")
    messages = [
        {
            "role": "user",
            "content": system_prompt,
        }
    ]
    print("Enter 'exit' to exit chatbot")
    user_prompt = input(">>> ")
    while user_prompt not in ["exit"]:
        messages.append({"role": "user", "content": user_prompt})
        tool_loop(model, messages, tools)
        print()
        user_prompt = input(">>> ")
