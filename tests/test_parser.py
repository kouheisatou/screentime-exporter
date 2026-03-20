"""Tests for the parser module."""

import pytest
from datetime import date

from screentime_exporter.parser import (
    parse_duration,
    parse_screen_time_text,
    AppUsage,
)


class TestParseDuration:
    """Tests for parse_duration function."""
    
    def test_japanese_hours_and_minutes(self):
        assert parse_duration("1時間30分") == 90
        assert parse_duration("2時間15分") == 135
        
    def test_japanese_hours_only(self):
        assert parse_duration("2時間") == 120
        assert parse_duration("1時間") == 60
        
    def test_japanese_minutes_only(self):
        assert parse_duration("45分") == 45
        assert parse_duration("5分") == 5
        
    def test_english_hours_and_minutes(self):
        assert parse_duration("1 hr 30 min") == 90
        assert parse_duration("2 hours 15 minutes") == 135
        
    def test_english_hours_only(self):
        assert parse_duration("2 hr") == 120
        assert parse_duration("1 hour") == 60
        
    def test_english_minutes_only(self):
        assert parse_duration("45 min") == 45
        assert parse_duration("5 minutes") == 5
        
    def test_time_format(self):
        assert parse_duration("1:30") == 90
        assert parse_duration("2:15") == 135
        assert parse_duration("0:45") == 45
        
    def test_with_whitespace(self):
        assert parse_duration("  1時間30分  ") == 90
        assert parse_duration("1 時間 30 分") == 90
        
    def test_invalid_format(self):
        assert parse_duration("invalid") == 0
        assert parse_duration("") == 0


class TestParseScreenTimeText:
    """Tests for parse_screen_time_text function."""
    
    def test_basic_app_list(self):
        lines = [
            "Twitter 45分",
            "LINE 30分",
            "Safari 1時間",
        ]
        result = parse_screen_time_text(lines, date(2026, 3, 1))
        
        assert result.date == date(2026, 3, 1)
        assert len(result.apps) == 3
        assert result.total_minutes == 135
        
    def test_with_categories(self):
        lines = [
            "ソーシャルネットワーキング 1時間15分",
            "Twitter 45分",
            "LINE 30分",
            "仕事効率化 2時間",
            "Slack 1時間30分",
            "Notion 30分",
        ]
        result = parse_screen_time_text(lines, date(2026, 3, 1))
        
        assert "ソーシャルネットワーキング" in result.categories
        assert "仕事効率化" in result.categories
        
    def test_filters_total_entries(self):
        lines = [
            "Twitter 45分",
            "合計 2時間",
            "LINE 30分",
        ]
        result = parse_screen_time_text(lines, date(2026, 3, 1))
        
        # Should not include "合計" as an app
        app_names = [app.app_name for app in result.apps]
        assert "合計" not in app_names
        assert len(result.apps) == 2
        
    def test_english_format(self):
        lines = [
            "Twitter 45 min",
            "Safari 1 hr 30 min",
        ]
        result = parse_screen_time_text(lines, date(2026, 3, 1))
        
        assert len(result.apps) == 2
        assert result.total_minutes == 135
