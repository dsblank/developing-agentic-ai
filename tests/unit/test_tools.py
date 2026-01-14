"""Unit tests for tools module."""

import json
from unittest.mock import Mock, patch

import pytest
import requests

from developing_agentic_ai.tools import filter_info, get_weather


class TestFilterInfo:
    """Tests for filter_info function."""

    def test_filter_info_complete(self):
        """Test filtering complete location data."""
        data = {
            "name": "Boston",
            "admin1": "Massachusetts",
            "country": "United States",
        }
        result = filter_info(data)
        assert result == {
            "city": "Boston",
            "state": "Massachusetts",
            "country": "United States",
        }

    def test_filter_info_missing_state(self):
        """Test filtering data without state."""
        data = {"name": "Paris", "country": "France"}
        result = filter_info(data)
        assert result == {"city": "Paris", "state": None, "country": "France"}

    def test_filter_info_missing_country(self):
        """Test filtering data without country."""
        data = {"name": "Boston", "admin1": "Massachusetts"}
        result = filter_info(data)
        assert result == {"city": "Boston", "state": "Massachusetts", "country": ""}


class TestGetWeather:
    """Tests for get_weather function."""

    @patch("developing_agentic_ai.tools.requests.get")
    def test_get_weather_success(self, mock_get):
        """Test successful weather retrieval."""
        # Mock geocoding response
        mock_geo_resp = Mock()
        mock_geo_resp.json.return_value = {
            "results": [
                {
                    "name": "Boston",
                    "admin1": "Massachusetts",
                    "country": "United States",
                    "latitude": 42.3601,
                    "longitude": -71.0589,
                }
            ]
        }
        mock_geo_resp.raise_for_status = Mock()

        # Mock weather response
        mock_weather_resp = Mock()
        mock_weather_resp.json.return_value = {
            "current_weather": {"temperature": 20.0, "windspeed": 10.5}
        }
        mock_weather_resp.raise_for_status = Mock()

        mock_get.side_effect = [mock_geo_resp, mock_weather_resp]

        result = get_weather("Boston", country="United States")
        result_dict = json.loads(result)

        assert result_dict["city"] == "Boston"
        assert result_dict["state"] == "Massachusetts"
        assert result_dict["country"] == "United States"
        assert result_dict["temperature"] == 68.0  # 20 * 1.8 + 32
        assert result_dict["temperature-units"] == "Fahrenheit"
        assert result_dict["windspeed"] == 10.5

    @patch("developing_agentic_ai.tools.requests.get")
    def test_get_weather_city_not_found(self, mock_get):
        """Test handling when city is not found."""
        mock_geo_resp = Mock()
        mock_geo_resp.json.return_value = {"results": []}
        mock_geo_resp.raise_for_status = Mock()
        mock_get.return_value = mock_geo_resp

        result = get_weather("NonexistentCity")
        assert "not found" in result.lower()

    @patch("developing_agentic_ai.tools.requests.get")
    def test_get_weather_multiple_matches(self, mock_get):
        """Test handling multiple city matches when filters don't match."""
        # When filters don't match any result, function returns list of all matches
        mock_geo_resp = Mock()
        mock_geo_resp.json.return_value = {
            "results": [
                {
                    "name": "Johnson City",
                    "admin1": "Tennessee",
                    "country": "United States",
                    "latitude": 36.3134,
                    "longitude": -82.3535,
                },
                {
                    "name": "Johnson City",
                    "admin1": "Texas",
                    "country": "United States",
                    "latitude": 30.2766,
                    "longitude": -98.4117,
                },
            ]
        }
        mock_geo_resp.raise_for_status = Mock()
        mock_get.return_value = mock_geo_resp

        # Use a filter that doesn't match any result
        result = get_weather("Johnson City", state="California")
        result_list = json.loads(result)

        assert isinstance(result_list, list)
        assert len(result_list) == 2
        assert result_list[0]["city"] == "Johnson City"
        assert result_list[1]["city"] == "Johnson City"
        # Should only call geocoding API, not weather API when no match
        assert mock_get.call_count == 1

    @patch("developing_agentic_ai.tools.requests.get")
    def test_get_weather_with_state_filter(self, mock_get):
        """Test filtering by state."""
        mock_geo_resp = Mock()
        mock_geo_resp.json.return_value = {
            "results": [
                {
                    "name": "Boston",
                    "admin1": "Massachusetts",
                    "country": "United States",
                    "latitude": 42.3601,
                    "longitude": -71.0589,
                },
                {
                    "name": "Boston",
                    "admin1": "Lincolnshire",
                    "country": "United Kingdom",
                    "latitude": 52.9789,
                    "longitude": -0.0266,
                },
            ]
        }
        mock_geo_resp.raise_for_status = Mock()

        mock_weather_resp = Mock()
        mock_weather_resp.json.return_value = {
            "current_weather": {"temperature": 20.0, "windspeed": 10.5}
        }
        mock_weather_resp.raise_for_status = Mock()

        mock_get.side_effect = [mock_geo_resp, mock_weather_resp]

        result = get_weather("Boston", state="Massachusetts")
        result_dict = json.loads(result)

        assert result_dict["city"] == "Boston"
        assert result_dict["state"] == "Massachusetts"
        assert result_dict["country"] == "United States"

    @patch("developing_agentic_ai.tools.requests.get")
    def test_get_weather_with_country_filter(self, mock_get):
        """Test filtering by country."""
        mock_geo_resp = Mock()
        mock_geo_resp.json.return_value = {
            "results": [
                {
                    "name": "Paris",
                    "admin1": "Île-de-France",
                    "country": "France",
                    "latitude": 48.8566,
                    "longitude": 2.3522,
                },
                {
                    "name": "Paris",
                    "admin1": "Texas",
                    "country": "United States",
                    "latitude": 33.6618,
                    "longitude": -95.5555,
                },
            ]
        }
        mock_geo_resp.raise_for_status = Mock()

        mock_weather_resp = Mock()
        mock_weather_resp.json.return_value = {
            "current_weather": {"temperature": 15.0, "windspeed": 8.0}
        }
        mock_weather_resp.raise_for_status = Mock()

        mock_get.side_effect = [mock_geo_resp, mock_weather_resp]

        result = get_weather("Paris", country="France")
        result_dict = json.loads(result)

        assert result_dict["city"] == "Paris"
        assert result_dict["country"] == "France"

    @patch("developing_agentic_ai.tools.requests.get")
    def test_get_weather_no_match_with_filters(self, mock_get):
        """Test when filters don't match any results."""
        mock_geo_resp = Mock()
        mock_geo_resp.json.return_value = {
            "results": [
                {
                    "name": "Boston",
                    "admin1": "Massachusetts",
                    "country": "United States",
                    "latitude": 42.3601,
                    "longitude": -71.0589,
                }
            ]
        }
        mock_geo_resp.raise_for_status = Mock()
        mock_get.return_value = mock_geo_resp

        result = get_weather("Boston", state="California")
        result_list = json.loads(result)

        # Should return list of all matches when filter doesn't match
        assert isinstance(result_list, list)
        assert len(result_list) == 1

    @patch("developing_agentic_ai.tools.requests.get")
    def test_get_weather_geocoding_error(self, mock_get):
        """Test handling geocoding API error."""
        mock_get.side_effect = requests.exceptions.HTTPError("API Error")

        with pytest.raises(requests.exceptions.HTTPError):
            get_weather("Boston")

    @patch("developing_agentic_ai.tools.requests.get")
    def test_get_weather_weather_api_error(self, mock_get):
        """Test handling weather API error."""
        mock_geo_resp = Mock()
        mock_geo_resp.json.return_value = {
            "results": [
                {
                    "name": "Boston",
                    "admin1": "Massachusetts",
                    "country": "United States",
                    "latitude": 42.3601,
                    "longitude": -71.0589,
                }
            ]
        }
        mock_geo_resp.raise_for_status = Mock()

        mock_weather_resp = Mock()
        mock_weather_resp.raise_for_status.side_effect = requests.exceptions.HTTPError("API Error")

        mock_get.side_effect = [mock_geo_resp, mock_weather_resp]

        with pytest.raises(requests.exceptions.HTTPError):
            get_weather("Boston")

    @patch("developing_agentic_ai.tools.requests.get")
    def test_get_weather_case_insensitive_filter(self, mock_get):
        """Test that state/country filters are case-insensitive."""
        mock_geo_resp = Mock()
        mock_geo_resp.json.return_value = {
            "results": [
                {
                    "name": "Boston",
                    "admin1": "Massachusetts",
                    "country": "United States",
                    "latitude": 42.3601,
                    "longitude": -71.0589,
                }
            ]
        }
        mock_geo_resp.raise_for_status = Mock()

        mock_weather_resp = Mock()
        mock_weather_resp.json.return_value = {
            "current_weather": {"temperature": 20.0, "windspeed": 10.5}
        }
        mock_weather_resp.raise_for_status = Mock()

        mock_get.side_effect = [mock_geo_resp, mock_weather_resp]

        # Test with lowercase filter
        result = get_weather("Boston", state="massachusetts", country="united states")
        result_dict = json.loads(result)

        assert result_dict["city"] == "Boston"
        assert result_dict["state"] == "Massachusetts"
