"""Parser module for extracting Screen Time data from OCR results."""

import re
from dataclasses import dataclass
from datetime import date


@dataclass
class AppUsage:
    """Represents usage data for a single app."""
    app_name: str
    duration_minutes: int
    category: str | None = None


@dataclass
class DailyScreenTime:
    """Represents Screen Time data for a single day."""
    date: date
    total_minutes: int
    apps: list[AppUsage]
    categories: dict[str, int]  # category -> minutes


def parse_duration(duration_str: str) -> int:
    """Parse a duration string into minutes.
    
    Supports formats like:
    - "1時間30分" -> 90
    - "45分" -> 45
    - "2時間" -> 120
    - "1 hr 30 min" -> 90
    - "45 min" -> 45
    - "2 hr" -> 120
    - "1:30" -> 90
    
    Args:
        duration_str: Duration string to parse
        
    Returns:
        Duration in minutes
    """
    duration_str = duration_str.strip()
    total_minutes = 0
    
    # Japanese format: X時間Y分
    jp_match = re.match(r"(\d+)\s*時間\s*(?:(\d+)\s*分)?", duration_str)
    if jp_match:
        hours = int(jp_match.group(1))
        minutes = int(jp_match.group(2)) if jp_match.group(2) else 0
        return hours * 60 + minutes
    
    # Japanese format: X分 (minutes only)
    jp_min_match = re.match(r"(\d+)\s*分", duration_str)
    if jp_min_match:
        return int(jp_min_match.group(1))
    
    # English format: X hr Y min or X hour Y minute
    en_match = re.match(r"(\d+)\s*(?:hr|hour)s?\s*(?:(\d+)\s*(?:min|minute)s?)?", duration_str, re.IGNORECASE)
    if en_match:
        hours = int(en_match.group(1))
        minutes = int(en_match.group(2)) if en_match.group(2) else 0
        return hours * 60 + minutes
    
    # English format: X min (minutes only)
    en_min_match = re.match(r"(\d+)\s*(?:min|minute)s?", duration_str, re.IGNORECASE)
    if en_min_match:
        return int(en_min_match.group(1))
    
    # Time format: H:MM
    time_match = re.match(r"(\d+):(\d{2})", duration_str)
    if time_match:
        hours = int(time_match.group(1))
        minutes = int(time_match.group(2))
        return hours * 60 + minutes
    
    return 0


def parse_screen_time_text(lines: list[str], target_date: date) -> DailyScreenTime:
    """Parse OCR text lines into structured Screen Time data.
    
    Args:
        lines: List of text lines from OCR
        target_date: The date this data represents
        
    Returns:
        Parsed Screen Time data
    """
    apps = []
    categories = {}
    total_minutes = 0
    
    # Known categories in Japanese and English
    known_categories = {
        # Japanese
        "ソーシャルネットワーキング": "ソーシャルネットワーキング",
        "エンターテイメント": "エンターテイメント",
        "仕事効率化": "仕事効率化",
        "クリエイティビティ": "クリエイティビティ",
        "ユーティリティ": "ユーティリティ",
        "情報と読書": "情報と読書",
        "ゲーム": "ゲーム",
        "教育": "教育",
        "健康とフィットネス": "健康とフィットネス",
        "その他": "その他",
        # English
        "Social Networking": "ソーシャルネットワーキング",
        "Social": "ソーシャルネットワーキング",
        "Entertainment": "エンターテイメント",
        "Productivity": "仕事効率化",
        "Creativity": "クリエイティビティ",
        "Utilities": "ユーティリティ",
        "Information & Reading": "情報と読書",
        "Reading & Reference": "情報と読書",
        "Games": "ゲーム",
        "Education": "教育",
        "Health & Fitness": "健康とフィットネス",
        "Other": "その他",
    }
    
    current_category = None
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Check if this line is a category
        for cat_name, normalized_cat in known_categories.items():
            if cat_name in line:
                current_category = normalized_cat
                # Try to extract duration from the same line or next line
                duration_match = re.search(r"(\d+\s*(?:時間|hr|hour)?\s*\d*\s*(?:分|min)?|\d+:\d{2})", line)
                if duration_match:
                    cat_duration = parse_duration(duration_match.group(1))
                    if cat_duration > 0:
                        categories[normalized_cat] = cat_duration
                break
        
        # Check if this line contains an app with duration
        # Pattern: AppName followed by duration
        app_pattern = re.search(
            r"^(.+?)\s+(\d+\s*(?:時間|hr|hour)?\s*\d*\s*(?:分|min)?|\d+:\d{2})$",
            line
        )
        if app_pattern:
            app_name = app_pattern.group(1).strip()
            duration_str = app_pattern.group(2)
            duration = parse_duration(duration_str)
            
            if duration > 0 and app_name:
                # Filter out non-app entries
                if not any(skip in app_name.lower() for skip in ["合計", "total", "平均", "average"]):
                    apps.append(AppUsage(
                        app_name=app_name,
                        duration_minutes=duration,
                        category=current_category,
                    ))
        
        i += 1
    
    # Calculate total from apps if not found
    if apps:
        total_minutes = sum(app.duration_minutes for app in apps)
    
    return DailyScreenTime(
        date=target_date,
        total_minutes=total_minutes,
        apps=apps,
        categories=categories,
    )


def parse_app_list(text: str, target_date: date) -> DailyScreenTime:
    """Parse text containing app usage list.
    
    Args:
        text: Full text from OCR
        target_date: The date this data represents
        
    Returns:
        Parsed Screen Time data
    """
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    return parse_screen_time_text(lines, target_date)
