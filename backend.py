"""
This module implements configuration, data retrieval, caching,
processing, reactive filtering, statistical summaries, visualizations,
and generated insights for the New York City crash analysis dashboard
built using Shiny for Python.
"""

import os
from dataclasses import dataclass
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import requests
import plotly.express as px

from shiny import reactive, render, ui
from shinywidgets import render_widget

from utils import (
    NYC_TZ,
    nyc_now,
    safe_int,
    normalize_str,
    parse_crash_date_to_nyc,
    derive_severity,
    risk_score,
    street_label,
    clean_for_json,
)


"""
Defines configuration values controlling API access, request limits,
caching duration, and visualization stability.
"""
BASE_URL = "https://data.cityofnewyork.us/resource/h9gi-nx95.json"
FETCH_LIMIT = 100_000
CACHE_TTL_MIN = 10
MAX_MAP_POINTS = 4000
SOCRATA_APP_TOKEN = os.getenv("SOCRATA_APP_TOKEN", "").strip()


"""
Represents a cached dataset together with the timestamp indicating
when the data was last retrieved.
"""
@dataclass
class CacheItem:
    fetched_at: datetime
    df: pd.DataFrame


"""
Stores cached crash datasets indexed by selected date ranges.
"""
_CACHE: dict[tuple[str, str], CacheItem] = {}


"""
Retrieves crash records from the NYC open data API for a specified
date range and prepares the dataset for analysis and visualization.
"""
def fetch_crashes(start_dt: datetime, end_dt: datetime) -> pd.DataFrame:
    where = (
        f"crash_date >= '{start_dt.date().isoformat()}' "
        f"AND crash_date <= '{end_dt.date().isoformat()}'"
    )
    params = {"$limit": FETCH_LIMIT, "$order": "crash_date DESC", "$where": where}

    headers = {}
    if SOCRATA_APP_TOKEN:
        headers["X-App-Token"] = SOCRATA_APP_TOKEN

    resp = requests.get(BASE_URL, params=params, headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    df = pd.DataFrame(data)
    if df.empty:
        return df

    numeric_cols = [
        "number_of_persons_injured", "number_of_persons_killed",
        "number_of_pedestrians_injured", "number_of_pedestrians_killed",
        "number_of_cyclist_injured", "number_of_cyclist_killed",
        "number_of_motorist_injured", "number_of_motorist_killed",
    ]

    for c in numeric_cols:
        if c not in df.columns:
            df[c] = 0
        df[c] = df[c].apply(safe_int)

    if "crash_date" in df.columns:
        df["crash_date"] = parse_crash_date_to_nyc(df["crash_date"])
    else:
        df["crash_date"] = pd.NaT

    if "crash_time" not in df.columns:
        df["crash_time"] = None

    def compute_hour(r):
        t = normalize_str(r.get("crash_time"))
        if t and ":" in t:
            try:
                hh = int(t.split(":")[0])
                if 0 <= hh <= 23:
                    return hh
            except Exception:
                pass
        cd = r.get("crash_date")
        try:
            return int(pd.Timestamp(cd).hour) if pd.notna(cd) else None
        except Exception:
            return None

    df["hour"] = df.apply(compute_hour, axis=1)
    df["weekday"] = df["crash_date"].dt.day_name()

    for c in ["borough", "zip_code", "on_street_name", "cross_street_name", "off_street_name"]:
        if c not in df.columns:
            df[c] = None

    for c in ["latitude", "longitude"]:
        if c not in df.columns:
            df[c] = np.nan
        df[c] = pd.to_numeric(df[c], errors="coerce")

    df["severity"] = derive_severity(df)
    df["risk_score"] = risk_score(df)
    df["street_label"] = df.apply(street_label, axis=1)

    df = clean_for_json(df)

    return df


"""
Returns crash data for the requested date range using cached results
when available, otherwise retrieving fresh data from the API.
"""
def get_cached_or_fetch(start_dt: datetime, end_dt: datetime) -> tuple[pd.DataFrame, str]:
    key = (start_dt.date().isoformat(), end_dt.date().isoformat())
    now = nyc_now()

    item = _CACHE.get(key)
    if item is not None:
        age_min = (now - item.fetched_at).total_seconds() / 60
        if age_min <= CACHE_TTL_MIN:
            return item.df.copy(), f"Cache hit ({age_min:.1f} min). Rows={len(item.df):,}"

    df = fetch_crashes(start_dt, end_dt)
    _CACHE[key] = CacheItem(fetched_at=now, df=df.copy())
    return df, f"Fetched fresh. Rows={len(df):,}"


"""
Defines the reactive server logic responsible for data loading,
filtering, KPI generation, visualizations, tabular summaries,
and analytical insights within the crash analysis dashboard.
"""
def server(input, output, session):

    """
    Stores the currently loaded dataset and related application state.
    """
    df_store = reactive.Value(pd.DataFrame())
    status_store = reactive.Value("Loading initial data...")
    last_range_store = reactive.Value("")
    did_initial_load = reactive.Value(False)

    """
    Determines the active date range selected by the user.
    """
    def _selected_range() -> tuple[datetime, datetime]:
        dr = input.dates()
        if not dr or dr[0] is None or dr[1] is None:
            end = nyc_now()
            start = end - timedelta(days=183)
            return start, end
        start = datetime.combine(dr[0], datetime.min.time(), tzinfo=NYC_TZ)
        end = datetime.combine(dr[1], datetime.max.time(), tzinfo=NYC_TZ)
        return start, end

    """
    Loads crash data for the selected range and updates user interface
    selections and status indicators.
    """
    def do_fetch():
        start, end = _selected_range()
        last_range_store.set(f"{start.date().isoformat()} → {end.date().isoformat()}")

        try:
            status_store.set("Fetching from API...")
            df, msg = get_cached_or_fetch(start, end)
            df_store.set(df)

            if df.empty or "borough" not in df.columns:
                ui.update_selectize("borough", choices=["All"], selected="All")
            else:
                boroughs = sorted([b for b in df["borough"].dropna().unique().tolist() if str(b).strip()])
                ui.update_selectize("borough", choices=["All"] + boroughs, selected="All")

            status_store.set(msg)
            ui.update_action_button("refresh", disabled=True)

        except requests.HTTPError as e:
            df_store.set(pd.DataFrame())
            status_store.set(f"HTTPError: {e}")
        except Exception as e:
            df_store.set(pd.DataFrame())
            status_store.set(f"Error: {type(e).__name__}: {e}")

    """
    Performs the automatic initial data load when the application starts.
    """
    @reactive.effect
    def _initial_load():
        if did_initial_load.get():
            return
        did_initial_load.set(True)
        do_fetch()

    """
    Reloads crash data when the refresh control is activated.
    """
    @reactive.effect
    @reactive.event(input.refresh)
    def _do_fetch():
        do_fetch()

    """
    Returns the dataset filtered by selected borough and severity.
    """
    @reactive.calc
    def filtered_data():
        df = df_store.get()
        if df.empty:
            return df

        b = input.borough()
        s = input.severity()

        if b and b != "All":
            df = df[df["borough"].fillna("").astype(str) == b]
        if s and s != "All":
            df = df[df["severity"] == s]

        return df

    """
    Displays the total number of crashes in the filtered dataset.
    """
    @output
    @render.text
    def kpi_total():
        df = filtered_data()
        return "0" if df.empty else f"{len(df):,}"

    """
    Displays the number of crashes involving injuries.
    """
    @output
    @render.text
    def kpi_injury():
        df = filtered_data()
        return "0" if df.empty else f"{(df['number_of_persons_injured'] > 0).sum():,}"

    """
    Displays the number of fatal crashes.
    """
    @output
    @render.text
    def kpi_fatal():
        df = filtered_data()
        return "0" if df.empty else f"{(df['number_of_persons_killed'] > 0).sum():,}"

    """
    Generates the daily crash time series chart for the selected filters.
    """
    @output
    @render_widget
    def ts_daily():
        df = filtered_data()
        if df.empty:
            return px.line(title="No data loaded")
        df = clean_for_json(df)

        daily = (
            df.dropna(subset=["crash_date"])
            .assign(day=lambda x: x["crash_date"].dt.date)
            .groupby("day").size()
            .reset_index(name="crashes")
            .sort_values("day")
        )
        fig = px.line(daily, x="day", y="crashes", title="Daily crashes")
        fig.update_layout(margin=dict(l=10, r=10, t=40, b=10))
        return fig

    """
    Generates the crash severity distribution bar chart for the selected filters.
    """
    @output
    @render_widget
    def sev_bar():
        df = filtered_data()
        if df.empty:
            return px.bar(title="No data loaded")
        df = clean_for_json(df)

        sev = df["severity"].value_counts().reindex(["Fatal", "Injury", "No Injury"], fill_value=0).reset_index()
        sev.columns = ["severity", "count"]
        fig = px.bar(sev, x="severity", y="count", title="Severity distribution")
        fig.update_layout(margin=dict(l=10, r=10, t=40, b=10))
        return fig

    """
    Generates the crash location map for the selected filters using available
    latitude and longitude values.
    """
    @output
    @render_widget
    def map_scatter():
        df = filtered_data()
        if df.empty:
            return px.scatter(title="No data loaded")

        df = clean_for_json(df)

        d = df.dropna(subset=["latitude", "longitude"]).copy()
        d = d[np.isfinite(d["latitude"]) & np.isfinite(d["longitude"])]

        d = d[
            (d["latitude"] >= 40.49) & (d["latitude"] <= 40.92) &
            (d["longitude"] >= -74.27) & (d["longitude"] <= -73.68)
        ]

        if d.empty:
            return px.scatter(title="No coordinates inside NYC bounds")

        if len(d) > MAX_MAP_POINTS:
            d = d.sample(MAX_MAP_POINTS, random_state=42)

        fig = px.scatter_mapbox(
            d,
            lat="latitude",
            lon="longitude",
            hover_name="street_label",
            color="severity",
            zoom=9,
            height=650,
            center={"lat": 40.7128, "lon": -74.0060},
            title=f"Crash locations (showing {len(d):,} points)",
        )
        fig.update_layout(mapbox_style="open-street-map", margin=dict(l=10, r=10, t=40, b=10))
        return fig

    """
    Generates a heatmap showing crash counts by weekday and hour for the
    selected filters.
    """
    @output
    @render_widget
    def heat_hour_day():
        df = filtered_data()
        if df.empty:
            return px.imshow([[0]], title="No data loaded")
        df = clean_for_json(df)

        d = df.dropna(subset=["hour", "weekday"]).copy()
        if d.empty:
            return px.imshow([[0]], title="No hour/weekday data available")

        weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        d["weekday"] = pd.Categorical(d["weekday"], categories=weekday_order, ordered=True)

        pivot = (
            d.groupby(["weekday", "hour"], observed=False).size().reset_index(name="count")
            .pivot(index="weekday", columns="hour", values="count")
            .fillna(0)
            .reindex(index=weekday_order)
        )

        fig = px.imshow(
            pivot,
            aspect="auto",
            title="Crashes by weekday and hour",
            labels=dict(x="Hour of day", y="Weekday", color="Crashes"),
        )
        fig.update_layout(margin=dict(l=10, r=10, t=40, b=10))
        return fig

    """
    Generates the crash counts by hour bar chart for the selected filters.
    """
    @output
    @render_widget
    def hourly_bar():
        df = filtered_data()
        if df.empty:
            return px.bar(title="No data loaded")
        df = clean_for_json(df)

        d = df.dropna(subset=["hour"]).copy()
        if d.empty:
            return px.bar(title="No hour data available")
        hourly = d.groupby("hour").size().reset_index(name="crashes").sort_values("hour")
        fig = px.bar(hourly, x="hour", y="crashes", title="Crashes by hour")
        fig.update_layout(margin=dict(l=10, r=10, t=40, b=10))
        return fig

    """
    Displays a table of streets or intersections with the highest crash counts
    together with injury and fatality totals.
    """
    @output
    @render.data_frame
    def top_streets_dt():
        df = filtered_data()
        if df.empty:
            empty = pd.DataFrame(columns=["Street / Intersection", "Crashes", "Injured", "Killed"])
            return render.DataGrid(empty, filters=True, height="340px")

        df = df[df["street_label"].notna()].copy()
        crash_count_col = "collision_id" if "collision_id" in df.columns else "severity"

        grp = (
            df.groupby("street_label", dropna=True)
            .agg(
                Crashes=(crash_count_col, "count"),
                Injured=("number_of_persons_injured", "sum"),
                Killed=("number_of_persons_killed", "sum"),
            )
            .reset_index()
            .rename(columns={"street_label": "Street / Intersection"})
            .sort_values(["Killed", "Injured", "Crashes"], ascending=False)
            .head(1000)
        )

        return render.DataGrid(grp, filters=True, height="340px")

    """
    Generates the risk score distribution histogram for the selected filters.
    """
    @output
    @render_widget
    def risk_hist():
        df = filtered_data()
        if df.empty:
            return px.histogram(title="No data loaded")
        df = clean_for_json(df)

        fig = px.histogram(df, x="risk_score", nbins=20, title="Risk score distribution")
        fig.update_layout(margin=dict(l=10, r=10, t=40, b=10))
        return fig

    """
    Generates the top contributing factors bar chart based on the primary
    contributing factor field.
    """
    @output
    @render_widget
    def top_factors():
        df = filtered_data()
        col = "contributing_factor_vehicle_1"
        if df.empty or col not in df.columns:
            return px.bar(title="No data loaded")
        df = clean_for_json(df)

        s = df[col].fillna("Unknown").astype(str).str.strip()
        top = s.value_counts().head(15).reset_index()
        top.columns = ["factor", "count"]
        fig = px.bar(top, x="count", y="factor", orientation="h", title="Top contributing factors")
        fig.update_layout(margin=dict(l=10, r=10, t=40, b=10), yaxis=dict(categoryorder="total ascending"))
        return fig

    """
    Generates the top vehicle types bar chart based on the primary vehicle type
    field.
    """
    @output
    @render_widget
    def top_vehicles():
        df = filtered_data()
        col = "vehicle_type_code1"
        if df.empty or col not in df.columns:
            return px.bar(title="No data loaded")
        df = clean_for_json(df)

        s = df[col].fillna("Unknown").astype(str).str.strip()
        top = s.value_counts().head(15).reset_index()
        top.columns = ["vehicle_type", "count"]
        fig = px.bar(top, x="count", y="vehicle_type", orientation="h", title="Top vehicle types")
        fig.update_layout(margin=dict(l=10, r=10, t=40, b=10), yaxis=dict(categoryorder="total ascending"))
        return fig

    """
    Generates a summary of key insights derived from the filtered dataset.
    """
    @output
    @render.ui
    def insights():
        df = filtered_data()
        if df.empty:
            return ui.p(
                {"style": "color: rgba(255,255,255,0.70); margin: 0;"},
                "No data loaded yet. Select a date range and click Apply."
            )

        total = len(df)
        injury = int((df["number_of_persons_injured"] > 0).sum())
        fatal = int((df["number_of_persons_killed"] > 0).sum())
        serious = injury + fatal
        serious_pct = (serious / total * 100.0) if total else 0.0

        peak_hour = None
        if "hour" in df.columns and df["hour"].notna().any():
            peak_hour = int(df.dropna(subset=["hour"]).groupby("hour").size().idxmax())

        worst_day = None
        if "weekday" in df.columns and df["weekday"].notna().any():
            worst_day = df["weekday"].value_counts().idxmax()

        top_borough = None
        if "borough" in df.columns and df["borough"].notna().any():
            vb = df["borough"].astype(str).str.strip()
            vb = vb[vb != ""]
            if not vb.empty:
                top_borough = vb.value_counts().idxmax()

        top_factor = None
        cf = "contributing_factor_vehicle_1"
        if cf in df.columns:
            s = df[cf].fillna("").astype(str).str.strip()
            bad = {"", "unknown", "unspecified", "other/unknown", "not stated"}
            s = s[~s.str.lower().isin(bad)]
            if not s.empty:
                top_factor = s.value_counts().idxmax()

        """
        Generates a borough-normalized crash rate chart for the selected filters.
        """
        @output
        @render_widget
        def borough_normalized_bar():
            df = filtered_data()
            if df.empty or "borough" not in df.columns:
                return px.bar(title="No data loaded")

            d = df.copy()
            d["borough"] = d["borough"].astype(str).str.strip()

            bad = {"", "Unknown", "UNKNOWN", "nan", "NaN", "None"}
            d = d[~d["borough"].isin(bad)]

            if d.empty:
                return px.bar(title="No valid borough data")

            days = d["crash_date"].dt.date.nunique()
            if days == 0:
                days = 1

            grp = (
                d.groupby("borough")
                .size()
                .reset_index(name="crashes")
            )
            grp["crashes_per_day"] = grp["crashes"] / days
            grp = grp.sort_values("crashes_per_day", ascending=False)

            fig = px.bar(
                grp,
                x="crashes_per_day",
                y="borough",
                orientation="h",
                title="Average Daily Crashes by Borough (Normalized)",
                labels={"crashes_per_day": "Crashes per day", "borough": "Borough"},
            )

            fig.update_layout(
                margin=dict(l=10, r=10, t=50, b=10),
                yaxis=dict(categoryorder="total ascending"),
            )

            return fig

        bullets = []
        bullets.append(f"Total crashes in the selected range: {total:,}.")
        bullets.append(f"Serious crashes (injury or fatal): {serious:,} ({serious_pct:.1f}%).")

        if peak_hour is not None:
            bullets.append(f"Peak crash hour: {peak_hour:02d}:00–{(peak_hour+1)%24:02d}:00.")
        if worst_day is not None:
            bullets.append(f"Highest-volume weekday: {worst_day}.")
        if top_borough is not None and top_borough != "nan":
            bullets.append(f"Highest-volume borough: {top_borough}.")
        if top_factor is not None:
            bullets.append(f"Most common contributing factor (Vehicle 1): {top_factor}.")

        return ui.tags.ul(
            {"style": "margin: 0; padding-left: 18px; color: rgba(255,255,255,0.90);"},
            *[ui.tags.li(b) for b in bullets[:5]]
        )
