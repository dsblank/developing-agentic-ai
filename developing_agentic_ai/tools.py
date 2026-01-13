import requests
import json
from typing import Optional, cast


def filter_info(data):
    return {
        "city": data["name"],
        "state": data.get("admin1"),
        "country": data.get("country", ""),
    }


def get_weather(city: str, state: Optional[str] = None, country: Optional[str] = None) -> str:
    """
    Get current weather for a city with optional state/country filtering.
    Falls back to first result if exact match not found.

    If you provide a state name or country, it must be the full name, no abreviations.

    If there are multiple matches, the funtion will return all matching cities.

    Examples:
    ```
    get_weather("Boston", country="United States")   # should match Boston, MA
    get_weather("Boston", country="United Kingdom")    # should match Boston, England
    get_weather("Paris")                   # will fallback to Paris, France
    get_weather("Johnson City")            # will return all matching cities
    ```
    """
    # Step 1: Geocode (search by city name only)
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"
    get_params: dict[str, str | int] = {"name": city, "count": 10}
    geo_resp = requests.get(geo_url, params=get_params)
    geo_resp.raise_for_status()
    geo_data = geo_resp.json()

    if "results" not in geo_data or not geo_data["results"]:
        return f"City '{city}' not found; try specifying city state/country in a different format"

    # Step 2: Filter by state/country if provided
    matches = geo_data["results"]
    chosen = None
    for place in matches:
        state_match = (not state) or (
            place.get("admin1") and state.lower() in place["admin1"].lower()
        )
        country_match = (not country) or (
            place.get("country") and country.lower() in place["country"].lower()
        )
        if state_match and country_match:
            chosen = place
            break

    if not chosen:
        # chosen = matches[0]
        return json.dumps([filter_info(match) for match in matches])

    lat, lon = chosen["latitude"], chosen["longitude"]

    # Step 3: Fetch current weather
    weather_url = "https://api.open-meteo.com/v1/forecast"
    params: dict[str, str | int | float | bool] = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True,
        "timezone": "auto",
    }
    weather_resp = requests.get(weather_url, params=params)
    weather_resp.raise_for_status()
    weather_data = weather_resp.json()

    # Step 4: Return structured result
    return json.dumps(
        {
            "city": chosen["name"],
            "state": chosen.get("admin1"),
            "country": chosen.get("country", ""),
            "temperature": weather_data["current_weather"]["temperature"],
            "windspeed": weather_data["current_weather"]["windspeed"],
        }
    )
