
"""
This module provides helper utilities for handling time zones, data cleaning,
string normalization, crash severity derivation, risk scoring, and safe data
preparation for JSON serialization in the New York City road safety dashboard.
"""

from datetime import datetime
from zoneinfo import ZoneInfo
import numpy as np
import pandas as pd


"""
Represents the time zone used for all New York City date and time operations.
"""
NYC_TZ = ZoneInfo("America/New_York")


def nyc_now() -> datetime:
    """
    Returns the current date and time localized to the New York City time zone.
    """
    return datetime.now(tz=NYC_TZ)


def safe_int(x) -> int:
    """
    Converts a value to an integer when possible and returns zero if conversion fails.
    """
    try:
        return int(float(x))
    except Exception:
        return 0


def normalize_str(x):
    """
    Produces a cleaned string value or returns None when the input is empty,
    missing, or represents a non-meaningful value.
    """
    if x is None:
        return None
    s = str(x).strip()
    if not s:
        return None
    if s.lower() == "nan":
        return None
    return s


def street_label(row: pd.Series) -> str | None:
    """
    Generates a readable street or intersection label from crash record fields
    when sufficient location information is available.
    """
    on_ = normalize_str(row.get("on_street_name"))
    cross_ = normalize_str(row.get("cross_street_name"))
    off_ = normalize_str(row.get("off_street_name"))

    if on_ and cross_:
        return f"{on_} @ {cross_}"
    if on_ and off_:
        return f"{on_} near {off_}"
    if on_:
        return on_
    return None


def derive_severity(df: pd.DataFrame) -> pd.Series:
    """
    Determines categorical crash severity levels based on counts of persons
    killed and injured within each crash record.
    """
    killed = df["number_of_persons_killed"].fillna(0).astype(int)
    injured = df["number_of_persons_injured"].fillna(0).astype(int)

    return np.select(
        [killed > 0, (killed == 0) & (injured > 0), (killed == 0) & (injured == 0)],
        ["Fatal", "Injury", "No Injury"],
        default="Unknown",
    )


def risk_score(df: pd.DataFrame) -> pd.Series:
    """
    Computes a numerical crash risk score using injury and fatality counts
    to support prioritization and ranking analyses.
    """
    killed = df["number_of_persons_killed"].fillna(0).astype(int)
    injured = df["number_of_persons_injured"].fillna(0).astype(int)
    return 5 * killed + 2 * injured + 1


def parse_crash_date_to_nyc(series: pd.Series) -> pd.Series:
    """
    Converts crash date values into timezone-aware timestamps aligned with the
    New York City time zone when valid date information is present.
    """
    dt = pd.to_datetime(series, errors="coerce")
    try:
        if getattr(dt.dt, "tz", None) is None:
            return dt.dt.tz_localize(NYC_TZ, nonexistent="shift_forward", ambiguous="NaT")
        return dt.dt.tz_convert(NYC_TZ)
    except Exception:
        return dt


def clean_for_json(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepares a dataframe for safe JSON serialization by normalizing missing
    values, ensuring string consistency, and converting numeric fields.
    """
    df = df.replace([np.inf, -np.inf], np.nan)

    for c in ["street_label", "borough", "severity", "weekday"]:
        if c in df.columns:
            df[c] = df[c].fillna("Unknown").astype(str)

    for c in [
        "latitude",
        "longitude",
        "risk_score",
        "number_of_persons_injured",
        "number_of_persons_killed",
        "hour",
    ]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    return df
