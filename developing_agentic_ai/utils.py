import inspect
import typing
from rich.console import Console
from rich.markdown import Markdown

console = Console()


def pretty_print(text: str) -> None:
    """
    Pretty print textual output.
    """
    # FIXME: assumes in_jupyter_environment
    console.print(Markdown(text))


def create_function_definition(func, description=None):
    sig = inspect.signature(func)
    doc = description or func.__doc__ or ""

    properties = {}
    required = []

    for name, param in sig.parameters.items():
        param_type = param.annotation if param.annotation != inspect.Parameter.empty else str
        json_type = python_type_to_json_type(param_type)
        properties[name] = {"type": json_type, "description": f"{name} parameter"}
        if param.default == inspect.Parameter.empty:
            required.append(name)

    return {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": doc.strip(),
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        },
    }


def python_type_to_json_type(python_type):
    # Basic type mapping
    if python_type in [str]:
        return "string"
    elif python_type in [int]:
        return "integer"
    elif python_type in [float]:
        return "number"
    elif python_type in [bool]:
        return "boolean"
    elif python_type in [dict]:
        return "object"
    elif python_type in [list, typing.List]:
        return "array"
    else:
        return "string"
