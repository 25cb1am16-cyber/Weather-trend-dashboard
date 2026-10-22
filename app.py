import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt

from datetime import date, timedelta
from weather_utils import (
    search_city,
    get_live_weather,
    get_historical_weather,
    weather_condition
)

st.set_page_config(
    page_title="Weather Trend Dashboard",
    page_icon="🌦️",
    layout="wide"
)

st.title("🌦️ Weather Trend Dashboard")
st.caption(
    "Live Weather | Historical Analysis | Forecast | City Comparison"
)

# Sidebar
st.sidebar.header("Dashboard Settings")

city = st.sidebar.text_input(
    "Search City", value="Gwalior"
).strip()

# City search
if not city:
    st.warning("Please enter a city name.")
    st.stop()

try:
    with st.spinner("Searching city and loading weather..."):
        location = search_city(city)

        if not location:
            st.error("City not found. Try another spelling.")
            st.stop()

        weather = get_live_weather(
            location["latitude"],
            location["longitude"],
            location.get("timezone", "auto")
        )

except Exception as e:
    st.error(f"Weather data could not be loaded: {e}")
    st.stop()

current = weather["current"]
hourly = weather["hourly"]
daily = weather["daily"]

st.subheader(
    f"📍 {location['name']}, "
    f"{location.get('country', '')}"
)

# Current weather cards
c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Temperature",
    f"{current['temperature_2m']} °C"
)
c2.metric(
    "Feels Like",
    f"{current['apparent_temperature']} °C"
)
c3.metric(
    "Humidity",
    f"{current['relative_humidity_2m']}%"
)
c4.metric(
    "Wind Speed",
    f"{current['wind_speed_10m']} km/h"
)

st.info(
    f"Condition: {weather_condition(current['weather_code'])}"
    f" | Precipitation: {current['precipitation']} mm"
)

# Prepare hourly and daily DataFrames
hourly_df = pd.DataFrame({
    "Time": pd.to_datetime(hourly["time"]),
    "Temperature": hourly["temperature_2m"],
    "Humidity": hourly["relative_humidity_2m"],
    "Rain Probability": hourly["precipitation_probability"],
    "Rainfall (mm)": hourly["precipitation"],
    "Wind Speed": hourly["wind_speed_10m"]
})

daily_df = pd.DataFrame({
    "Date": pd.to_datetime(daily["time"]),
    "Maximum Temperature": daily["temperature_2m_max"],
    "Minimum Temperature": daily["temperature_2m_min"],
    "Rainfall (mm)": daily["precipitation_sum"],
    "Weather Code": daily["weather_code"]
})

tabs = st.tabs([
    "Overview",
    "Trend Analysis",
    "7-Day Forecast",
    "Historical Weather",
    "City Comparison",
    "Download Data"
])

# TAB 1: OVERVIEW
with tabs[0]:
    st.subheader("Next 48 Hours Temperature Trend")

    fig = px.line(
        hourly_df.head(48),
        x="Time",
        y="Temperature",
        markers=True,
        title="Hourly Temperature"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Daily Weather Summary")

    daily_view = daily_df.copy()
    daily_view["Condition"] = daily_view[
        "Weather Code"
    ].apply(weather_condition)

    st.dataframe(
        daily_view.drop(columns=["Weather Code"]),
        use_container_width=True,
        hide_index=True
    )

# TAB 2: TREND ANALYSIS
with tabs[1]:
    st.subheader("Weather Parameter Analysis")

    parameter = st.selectbox(
        "Select Parameter",
        [
            "Temperature",
            "Humidity",
            "Rain Probability",
            "Rainfall (mm)",
            "Wind Speed"
        ]
    )

    fig = px.line(
        hourly_df.head(168),
        x="Time",
        y=parameter,
        markers=True,
        title=f"{parameter} Trend"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Maximum vs Minimum Temperature")

    fig2 = px.line(
        daily_df,
        x="Date",
        y=["Maximum Temperature", "Minimum Temperature"],
        markers=True,
        title="7-Day Temperature Comparison"
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Matplotlib Temperature Graph")

    fig3, ax = plt.subplots()

    ax.plot(
        daily_df["Date"],
        daily_df["Maximum Temperature"],
        marker="o",
        label="Maximum Temperature"
    )

    ax.plot(
        daily_df["Date"],
        daily_df["Minimum Temperature"],
        marker="o",
        label="Minimum Temperature"
    )

    ax.set_xlabel("Date")
    ax.set_ylabel("Temperature (°C)")
    ax.set_title("Temperature Analysis")
    ax.legend()
    ax.grid(True)
    plt.xticks(rotation=30)
    plt.tight_layout()

    st.pyplot(fig3)
    plt.close(fig3)

# TAB 3: FORECAST
with tabs[2]:
    st.subheader("7-Day Weather Forecast")

    forecast_df = daily_df.copy()
    forecast_df["Condition"] = forecast_df[
        "Weather Code"
    ].apply(weather_condition)

    st.dataframe(
        forecast_df.drop(columns=["Weather Code"]),
        use_container_width=True,
        hide_index=True
    )

    fig = px.bar(
        forecast_df,
        x="Date",
        y="Rainfall (mm)",
        title="Daily Rainfall Forecast"
    )
    st.plotly_chart(fig, use_container_width=True)

# TAB 4: HISTORICAL WEATHER
with tabs[3]:
    st.subheader("Historical Weather Search")

    st.write(
        "Select a date range to retrieve historical weather "
        "for the city searched above."
    )

    today = date.today()
    default_end = today - timedelta(days=6)
    default_start = default_end - timedelta(days=29)

    start_date = st.date_input(
        "Start Date",
        value=default_start,
        min_value=date(1940, 1, 1),
        max_value=default_end
    )

    end_date = st.date_input(
        "End Date",
        value=default_end,
        min_value=date(1940, 1, 1),
        max_value=default_end
    )

    if st.button("Fetch Historical Weather"):
        if start_date > end_date:
            st.error("Start date must be before end date.")

        else:
            try:
                with st.spinner("Fetching historical records..."):
                    history_df = get_historical_weather(
                        location["latitude"],
                        location["longitude"],
                        start_date.isoformat(),
                        end_date.isoformat(),
                        location.get("timezone", "auto")
                    )

                if history_df.empty:
                    st.warning("No historical records available.")

                else:
                    history_df = history_df.dropna(
                        subset=["Date"]
                    )

                    st.success(
                        f"Loaded {len(history_df)} daily records."
                    )

                    st.dataframe(
                        history_df,
                        use_container_width=True,
                        hide_index=True
                    )

                    fig = px.line(
                        history_df,
                        x="Date",
                        y=[
                            "Maximum Temperature",
                            "Minimum Temperature"
                        ],
                        title="Historical Temperature Trend"
                    )
                    st.plotly_chart(
                        fig, use_container_width=True
                    )

                    # Monthly aggregation
                    monthly_df = history_df.copy()
                    monthly_df["Month"] = (
                        monthly_df["Date"].dt.to_period("M").astype(str)
                    )

                    monthly_avg = (
                        monthly_df.groupby("Month", as_index=False)
                        [["Maximum Temperature", "Minimum Temperature"]]
                        .mean()
                    )

                    st.subheader("Monthly Average Temperatures")

                    fig2 = px.line(
                        monthly_avg,
                        x="Month",
                        y=[
                            "Maximum Temperature",
                            "Minimum Temperature"
                        ],
                        markers=True
                    )
                    st.plotly_chart(
                        fig2, use_container_width=True
                    )

                    # Yearly aggregation
                    yearly_df = history_df.copy()
                    yearly_df["Year"] = (
                        yearly_df["Date"].dt.year
                    )

                    yearly_avg = (
                        yearly_df.groupby("Year", as_index=False)
                        [["Maximum Temperature", "Minimum Temperature"]]
                        .mean()
                    )

                    st.subheader("Yearly Average Temperatures")

                    fig3 = px.bar(
                        yearly_avg,
                        x="Year",
                        y="Maximum Temperature",
                        title="Yearly Average Maximum Temperature"
                    )
                    st.plotly_chart(
                        fig3, use_container_width=True
                    )

                    st.download_button(
                        "Download Historical CSV",
                        data=history_df.to_csv(
                            index=False
                        ).encode("utf-8"),
                        file_name="historical_weather.csv",
                        mime="text/csv"
                    )

            except Exception as e:
                st.error(
                    f"Historical data could not be loaded: {e}"
                )

# TAB 5: CITY COMPARISON
with tabs[4]:
    st.subheader("Compare Multiple Cities")

    city_input = st.text_input(
        "Enter cities separated by commas",
        value="Delhi, Mumbai, Bhopal"
    )

    if st.button("Compare Weather"):
        names = [
            x.strip()
            for x in city_input.split(",")
            if x.strip()
        ]

        rows = []
        errors = []

        for name in dict.fromkeys(names):
            try:
                loc = search_city(name)

                if not loc:
                    errors.append(f"{name}: city not found")
                    continue

                result = get_live_weather(
                    loc["latitude"],
                    loc["longitude"],
                    loc.get("timezone", "auto")
                )

                cur = result["current"]

                rows.append({
                    "City": loc["name"],
                    "Country": loc.get("country", ""),
                    "Temperature": cur["temperature_2m"],
                    "Humidity": cur["relative_humidity_2m"],
                    "Wind Speed": cur["wind_speed_10m"]
                })

            except Exception:
                errors.append(f"{name}: data unavailable")

        if rows:
            comparison_df = pd.DataFrame(rows)

            fig = px.bar(
                comparison_df,
                x="City",
                y="Temperature",
                color="Temperature",
                hover_data=[
                    "Country",
                    "Humidity",
                    "Wind Speed"
                ],
                title="Current City Temperature Comparison"
            )

            st.plotly_chart(
                fig, use_container_width=True
            )

            st.dataframe(
                comparison_df,
                use_container_width=True,
                hide_index=True
            )

        for error in errors:
            st.warning(error)

# TAB 6: DOWNLOAD
with tabs[5]:
    st.subheader("Export Weather Data")

    st.download_button(
        "Download Hourly Weather CSV",
        data=hourly_df.to_csv(index=False).encode("utf-8"),
        file_name="hourly_weather.csv",
        mime="text/csv"
    )

    st.download_button(
        "Download 7-Day Forecast CSV",
        data=daily_df.to_csv(index=False).encode("utf-8"),
        file_name="weather_forecast.csv",
        mime="text/csv"
    )

st.divider()

st.caption(
    "Weather data provided by Open-Meteo. "
    "Forecasts are estimates, not guarantees."
)