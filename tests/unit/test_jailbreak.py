"""Unit tests for jailbreak dataset module."""

from unittest.mock import Mock, patch

from developing_agentic_ai.datasets.jailbreak import (
    create_jailbreak_dataset,
    jailbreak_prompts,
)


class TestJailbreakPrompts:
    """Tests for jailbreak_prompts list."""

    def test_prompts_not_empty(self):
        """Test that jailbreak_prompts list is not empty."""
        assert len(jailbreak_prompts) > 0

    def test_prompts_are_strings(self):
        """Test that all prompts are strings."""
        for prompt in jailbreak_prompts:
            assert isinstance(prompt, str)
            assert len(prompt) > 0

    def test_prompts_count(self):
        """Test expected number of prompts."""
        # Based on the actual code, there are 123 prompts
        assert len(jailbreak_prompts) == 123

    def test_prompts_unique(self):
        """Test that prompts are unique."""
        assert len(jailbreak_prompts) == len(set(jailbreak_prompts))


class TestCreateJailbreakDataset:
    """Tests for create_jailbreak_dataset function."""

    @patch("opik.Opik")
    def test_create_dataset_success(self, mock_opik_class):
        """Test successful dataset creation."""
        # Mock Opik client
        mock_client = Mock()
        mock_dataset = Mock()
        mock_dataset.id = "test-dataset-id"
        mock_client.get_or_create_dataset.return_value = mock_dataset
        mock_opik_class.return_value = mock_client

        create_jailbreak_dataset()

        # Verify client was initialized
        mock_opik_class.assert_called_once()

        # Verify dataset was created/get with correct name and description
        mock_client.get_or_create_dataset.assert_called_once()
        call_kwargs = mock_client.get_or_create_dataset.call_args[1]
        assert call_kwargs["name"] == "Jailbreak Dataset"
        assert "jailbreak" in call_kwargs["description"].lower()

        # Verify items were inserted
        mock_dataset.insert.assert_called_once()
        inserted_items = mock_dataset.insert.call_args[0][0]
        assert len(inserted_items) == len(jailbreak_prompts)

    @patch("opik.Opik")
    def test_dataset_items_structure(self, mock_opik_class):
        """Test that dataset items have correct structure."""
        mock_client = Mock()
        mock_dataset = Mock()
        mock_client.get_or_create_dataset.return_value = mock_dataset
        mock_opik_class.return_value = mock_client

        create_jailbreak_dataset()

        inserted_items = mock_dataset.insert.call_args[0][0]

        # Check structure of first few items
        for item in inserted_items[:10]:
            assert "question" in item
            assert "category" in item
            assert isinstance(item["question"], str)
            assert isinstance(item["category"], str)
            assert item["category"] in [
                "obfuscation",
                "role_play",
                "emotional_manipulation",
                "logic_manipulation",
                "system_override",
            ]

    @patch("opik.Opik")
    def test_dataset_categories(self, mock_opik_class):
        """Test that prompts are categorized correctly."""
        mock_client = Mock()
        mock_dataset = Mock()
        mock_client.get_or_create_dataset.return_value = mock_dataset
        mock_opik_class.return_value = mock_client

        create_jailbreak_dataset()

        inserted_items = mock_dataset.insert.call_args[0][0]

        # Check category distribution
        categories = [item["category"] for item in inserted_items]
        assert categories[0] == "obfuscation"  # First 25
        assert categories[24] == "obfuscation"
        assert categories[25] == "role_play"  # 26-50
        assert categories[49] == "role_play"
        assert categories[50] == "emotional_manipulation"  # 51-75
        assert categories[74] == "emotional_manipulation"
        assert categories[75] == "logic_manipulation"  # 76-100
        assert categories[99] == "logic_manipulation"
        assert categories[100] == "system_override"  # 101-123
        assert categories[-1] == "system_override"

    @patch("opik.Opik")
    def test_dataset_items_match_prompts(self, mock_opik_class):
        """Test that dataset items match the prompts."""
        mock_client = Mock()
        mock_dataset = Mock()
        mock_client.get_or_create_dataset.return_value = mock_dataset
        mock_opik_class.return_value = mock_client

        create_jailbreak_dataset()

        inserted_items = mock_dataset.insert.call_args[0][0]

        # Verify each prompt is in the dataset
        for i, prompt in enumerate(jailbreak_prompts):
            assert inserted_items[i]["question"] == prompt

    @patch("opik.Opik")
    def test_create_dataset_handles_existing_dataset(self, mock_opik_class):
        """Test that function handles existing dataset gracefully."""
        mock_client = Mock()
        mock_dataset = Mock()
        mock_dataset.id = "existing-dataset-id"
        mock_client.get_or_create_dataset.return_value = mock_dataset
        mock_opik_class.return_value = mock_client

        # Should not raise exception
        create_jailbreak_dataset()

        mock_client.get_or_create_dataset.assert_called_once()
