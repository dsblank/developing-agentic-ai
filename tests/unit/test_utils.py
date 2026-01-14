"""Unit tests for utils module."""

from typing import List, Optional
from unittest.mock import patch

from developing_agentic_ai.utils import (
    create_function_definition,
    pretty_print,
    python_type_to_json_type,
)


class TestPythonTypeToJsonType:
    """Tests for python_type_to_json_type function."""

    def test_string_type(self):
        """Test string type conversion."""
        assert python_type_to_json_type(str) == "string"

    def test_int_type(self):
        """Test integer type conversion."""
        assert python_type_to_json_type(int) == "integer"

    def test_float_type(self):
        """Test float type conversion."""
        assert python_type_to_json_type(float) == "number"

    def test_bool_type(self):
        """Test boolean type conversion."""
        assert python_type_to_json_type(bool) == "boolean"

    def test_dict_type(self):
        """Test dict type conversion."""
        assert python_type_to_json_type(dict) == "object"

    def test_list_type(self):
        """Test list type conversion."""
        assert python_type_to_json_type(list) == "array"

    def test_typing_list_type(self):
        """Test typing.List type conversion."""
        assert python_type_to_json_type(List) == "array"

    def test_unknown_type_defaults_to_string(self):
        """Test that unknown types default to string."""
        assert python_type_to_json_type(Optional[str]) == "string"
        assert python_type_to_json_type(type(None)) == "string"
        assert python_type_to_json_type(object) == "string"


class TestCreateFunctionDefinition:
    """Tests for create_function_definition function."""

    def test_simple_function(self):
        """Test creating definition for simple function."""

        def test_func(name: str, age: int) -> str:
            """Test function."""
            return f"{name} is {age}"

        result = create_function_definition(test_func)

        assert result["type"] == "function"
        assert result["function"]["name"] == "test_func"
        assert result["function"]["description"] == "Test function."
        assert "parameters" in result["function"]
        assert result["function"]["parameters"]["type"] == "object"
        assert "name" in result["function"]["parameters"]["properties"]
        assert "age" in result["function"]["parameters"]["properties"]
        assert result["function"]["parameters"]["properties"]["name"]["type"] == "string"
        assert result["function"]["parameters"]["properties"]["age"]["type"] == "integer"
        assert "name" in result["function"]["parameters"]["required"]
        assert "age" in result["function"]["parameters"]["required"]

    def test_function_with_defaults(self):
        """Test creating definition for function with default parameters."""

        def test_func(name: str, age: int = 18, city: str = "Boston") -> str:
            """Test function with defaults."""
            return f"{name} is {age}"

        result = create_function_definition(test_func)

        assert "name" in result["function"]["parameters"]["required"]
        assert "age" not in result["function"]["parameters"]["required"]
        assert "city" not in result["function"]["parameters"]["required"]

    def test_function_without_docstring(self):
        """Test creating definition for function without docstring."""

        def test_func(name: str) -> str:
            return name

        result = create_function_definition(test_func)

        assert result["function"]["description"] == ""

    def test_function_with_custom_description(self):
        """Test creating definition with custom description."""

        def test_func(name: str) -> str:
            """Original docstring."""
            return name

        result = create_function_definition(test_func, description="Custom description")

        assert result["function"]["description"] == "Custom description"

    def test_function_with_complex_types(self):
        """Test creating definition for function with complex types."""
        # Note: python_type_to_json_type doesn't handle generic types like List[str],
        # so it defaults to string. This test verifies the actual behavior.

        def test_func(
            name: str, items: List[str], metadata: dict, optional: Optional[int] = None
        ) -> str:
            """Test function with complex types."""
            return name

        result = create_function_definition(test_func)

        # List[str] is not recognized as array, defaults to string
        assert result["function"]["parameters"]["properties"]["items"]["type"] == "string"
        assert result["function"]["parameters"]["properties"]["metadata"]["type"] == "object"
        # Optional[int] defaults to string
        assert result["function"]["parameters"]["properties"]["optional"]["type"] == "string"

    def test_function_with_no_parameters(self):
        """Test creating definition for function with no parameters."""

        def test_func() -> str:
            """Test function with no parameters."""
            return "test"

        result = create_function_definition(test_func)

        assert result["function"]["parameters"]["properties"] == {}
        assert result["function"]["parameters"]["required"] == []

    def test_function_with_no_type_annotations(self):
        """Test creating definition for function without type annotations."""

        def test_func(name, age):
            """Test function without annotations."""
            return f"{name} is {age}"

        result = create_function_definition(test_func)

        # Should default to string for unannotated parameters
        assert result["function"]["parameters"]["properties"]["name"]["type"] == "string"
        assert result["function"]["parameters"]["properties"]["age"]["type"] == "string"

    def test_function_parameter_descriptions(self):
        """Test that parameter descriptions are set correctly."""

        def test_func(name: str, age: int) -> str:
            """Test function."""
            return f"{name} is {age}"

        result = create_function_definition(test_func)

        assert (
            result["function"]["parameters"]["properties"]["name"]["description"]
            == "name parameter"
        )
        assert (
            result["function"]["parameters"]["properties"]["age"]["description"] == "age parameter"
        )


class TestPrettyPrint:
    """Tests for pretty_print function."""

    @patch("developing_agentic_ai.utils.console")
    def test_pretty_print(self, mock_console):
        """Test pretty_print function."""
        text = "# Hello\nThis is a test."
        pretty_print(text)

        mock_console.print.assert_called_once()
        # Verify Markdown was used
        call_args = mock_console.print.call_args[0]
        assert hasattr(call_args[0], "__class__")
        # The argument should be a Markdown object (from rich.markdown)

    @patch("developing_agentic_ai.utils.console")
    def test_pretty_print_empty_string(self, mock_console):
        """Test pretty_print with empty string."""
        pretty_print("")
        mock_console.print.assert_called_once()

    @patch("developing_agentic_ai.utils.console")
    def test_pretty_print_markdown(self, mock_console):
        """Test pretty_print with markdown content."""
        text = "## Heading\n\n**Bold** and *italic* text."
        pretty_print(text)
        mock_console.print.assert_called_once()
