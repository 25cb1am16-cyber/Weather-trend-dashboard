import requests
import pandas as pd

GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"


def search_city(city):
    response = requests.get(
        GEO_URL,
        params={
            "name": city,
            "count": 1,
            "language": "en",
            "format": "json"
        },
        timeout=20
    )
    response.raise_for_status()

    results = response.json().get("results", [])

    if not results:
        return None

    return results[0]


def get_live_weather(latitude, longitude, timezone="auto"):
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "timezone": timezone,
        "current": (
            "temperature_2m,relative_humidity_2m,"
            "apparent_temperature,precipitation,"
            "wind_speed_10m,weather_code"
        ),
        "hourly": (
            "temperature_2m,relative_humidity_2m,"
            "precipitation_probability,precipitation,"
            "wind_speed_10m"
        ),
        "daily": (
            "weather_code,temperature_2m_max,"
            "temperature_2m_min,precipitation_sum,"
            "wind_speed_10m_max"
        ),
        "forecast_days": 7
    }

    response = requests.get(
        FORECAST_URL, params=params, timeout=30
    )
    response.raise_for_status()

    return response.json()


def get_historical_weather(
    latitude, longitude, start_date, end_date,
    timezone="auto"
):
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "daily": (
            "temperature_2m_max,"
            "temperature_2m_min,"
            "precipitation_sum"
        ),
        "timezone": timezone
    }

    response = requests.get(
        ARCHIVE_URL, params=params, timeout=60
    )
    response.raise_for_status()

    daily = response.json().get("daily", {})

    return pd.DataFrame({
        "Date": pd.to_datetime(daily.get("time", [])),
        "Maximum Temperature": daily.get(
            "temperature_2m_max", []
        ),
        "Minimum Temperature": daily.get(
            "temperature_2m_min", []
        ),
        "Rainfall (mm)": daily.get(
            "precipitation_sum", []
        )
    })


def weather_condition(code):
    conditions = {
        0: "Clear Sky",
        1: "Mainly Clear",
        2: "Partly Cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Fog",
        51: "Drizzle",
        53: "Drizzle",
        55: "Drizzle",
        61: "Rain",
        63: "Moderate Rain",
        65: "Heavy Rain",
        71: "Snow",
        73: "Snow",
        75: "Heavy Snow",
        80: "Rain Showers",
        81: "Rain Showers",
        82: "Heavy Showers",
        95: "Thunderstorm",
        96: "Thunderstorm",
        99: "Thunderstorm"
    }

    try:
        return conditions.get(int(code), "Other Conditions")
    except (ValueError, TypeError):
        return "Unknown"