"""Tests for the exporter module."""

import pytest
import tempfile
from datetime import date
from pathlib import Path

from screentime_exporter.exporter import to_dataframe, export_to_csv
from screentime_exporter.parser import DailyScreenTime, AppUsage


class TestToDataframe:
    """Tests for to_dataframe function."""
    
    def test_basic_conversion(self):
        daily_data = [
            DailyScreenTime(
                date=date(2026, 3, 1),
                total_minutes=120,
                apps=[
                    AppUsage("Twitter", 45, "ソーシャルネットワーキング"),
                    AppUsage("Safari", 75, "情報と読書"),
                ],
                categories={"ソーシャルネットワーキング": 45, "情報と読書": 75},
            )
        ]
        
        df = to_dataframe(daily_data)
        
        assert len(df) == 2
        assert "date" in df.columns
        assert "category" in df.columns
        assert "app_name" in df.columns
        assert "duration_minutes" in df.columns
        
    def test_multiple_days(self):
        daily_data = [
            DailyScreenTime(
                date=date(2026, 3, 1),
                total_minutes=60,
                apps=[AppUsage("Twitter", 60, "ソーシャルネットワーキング")],
                categories={},
            ),
            DailyScreenTime(
                date=date(2026, 3, 2),
                total_minutes=90,
                apps=[AppUsage("Safari", 90, "情報と読書")],
                categories={},
            ),
        ]
        
        df = to_dataframe(daily_data)
        
        assert len(df) == 2
        assert df.iloc[0]["date"] == "2026-03-01"
        assert df.iloc[1]["date"] == "2026-03-02"
        
    def test_empty_data(self):
        df = to_dataframe([])
        assert len(df) == 0


class TestExportToCsv:
    """Tests for export_to_csv function."""
    
    def test_export_creates_file(self):
        daily_data = [
            DailyScreenTime(
                date=date(2026, 3, 1),
                total_minutes=60,
                apps=[AppUsage("Twitter", 60, "ソーシャルネットワーキング")],
                categories={},
            )
        ]
        
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            output_path = Path(f.name)
        
        try:
            export_to_csv(daily_data, output_path)
            
            assert output_path.exists()
            content = output_path.read_text()
            assert "date" in content
            assert "Twitter" in content
            assert "2026-03-01" in content
        finally:
            output_path.unlink(missing_ok=True)
