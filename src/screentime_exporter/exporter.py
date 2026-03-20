"""Exporter module for writing Screen Time data to CSV."""

import csv
from pathlib import Path

import pandas as pd

from .parser import DailyScreenTime


def to_dataframe(daily_data: list[DailyScreenTime]) -> pd.DataFrame:
    """Convert a list of daily Screen Time data to a pandas DataFrame.
    
    Args:
        daily_data: List of DailyScreenTime objects
        
    Returns:
        DataFrame with columns: date, category, app_name, duration_minutes
    """
    rows = []
    
    for day in daily_data:
        for app in day.apps:
            rows.append({
                "date": day.date.isoformat(),
                "category": app.category or "不明",
                "app_name": app.app_name,
                "duration_minutes": app.duration_minutes,
            })
    
    df = pd.DataFrame(rows)
    
    if not df.empty:
        df = df.sort_values(["date", "category", "app_name"])
    
    return df


def to_category_summary(daily_data: list[DailyScreenTime]) -> pd.DataFrame:
    """Create a summary DataFrame by category.
    
    Args:
        daily_data: List of DailyScreenTime objects
        
    Returns:
        DataFrame with columns: date, category, total_minutes
    """
    rows = []
    
    for day in daily_data:
        for category, minutes in day.categories.items():
            rows.append({
                "date": day.date.isoformat(),
                "category": category,
                "total_minutes": minutes,
            })
    
    df = pd.DataFrame(rows)
    
    if not df.empty:
        df = df.sort_values(["date", "category"])
    
    return df


def export_to_csv(
    daily_data: list[DailyScreenTime],
    output_path: Path,
    include_summary: bool = True,
) -> None:
    """Export Screen Time data to CSV file.
    
    Args:
        daily_data: List of DailyScreenTime objects
        output_path: Path to output CSV file
        include_summary: Whether to include category summary rows
    """
    df = to_dataframe(daily_data)
    df.to_csv(output_path, index=False, encoding="utf-8")


def export_summary_csv(
    daily_data: list[DailyScreenTime],
    output_path: Path,
) -> None:
    """Export category summary to CSV file.
    
    Args:
        daily_data: List of DailyScreenTime objects
        output_path: Path to output CSV file
    """
    df = to_category_summary(daily_data)
    df.to_csv(output_path, index=False, encoding="utf-8")


def export_detailed_csv(
    daily_data: list[DailyScreenTime],
    output_path: Path,
) -> None:
    """Export detailed app usage to CSV with additional statistics.
    
    Args:
        daily_data: List of DailyScreenTime objects
        output_path: Path to output CSV file
    """
    rows = []
    
    for day in daily_data:
        for app in day.apps:
            rows.append({
                "date": day.date.isoformat(),
                "category": app.category or "不明",
                "app_name": app.app_name,
                "duration_minutes": app.duration_minutes,
                "duration_hours": round(app.duration_minutes / 60, 2),
                "daily_total_minutes": day.total_minutes,
                "percentage_of_day": round(
                    app.duration_minutes / day.total_minutes * 100, 1
                ) if day.total_minutes > 0 else 0,
            })
    
    df = pd.DataFrame(rows)
    
    if not df.empty:
        df = df.sort_values(["date", "duration_minutes"], ascending=[True, False])
    
    df.to_csv(output_path, index=False, encoding="utf-8")
