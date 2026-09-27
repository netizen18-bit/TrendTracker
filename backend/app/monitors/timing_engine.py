import datetime
from typing import Optional, Tuple, Dict, Any, List
from dateutil import parser as date_parser

def normalize_datetime(dt: Any) -> Optional[datetime.datetime]:
    """Ensures datetime is timezone-aware in UTC."""
    if dt is None:
        return None
    
    if isinstance(dt, str):
        try:
            dt = date_parser.parse(dt)
        except Exception:
            return None

    if isinstance(dt, datetime.datetime):
        if dt.tzinfo is None:
            # Treat naive datetime as UTC
            dt = dt.replace(tzinfo=datetime.timezone.utc)
        else:
            dt = dt.astimezone(datetime.timezone.utc)
        return dt
    
    return None

def calculate_detection_delay(
    published_at: Optional[datetime.datetime],
    detected_at: Optional[datetime.datetime] = None
) -> Tuple[Optional[float], Optional[str]]:
    """
    Calculates exact detection delay in seconds and human-readable string.
    delay = detected_at - published_at
    """
    if detected_at is None:
        detected_at = datetime.datetime.now(datetime.timezone.utc)
    else:
        detected_at = normalize_datetime(detected_at)

    published_at = normalize_datetime(published_at)

    if not published_at or not detected_at:
        return None, "Unknown"

    delay_seconds = (detected_at - published_at).total_seconds()
    
    # Handle minor clock drift if detected is slightly before published
    if delay_seconds < 0:
        delay_seconds = 0.0

    formatted = format_delay(delay_seconds)
    return delay_seconds, formatted

def format_delay(seconds: float) -> str:
    """Formats seconds into readable format: 47s, 3m 12s, 1h 14m 22s."""
    seconds = int(round(seconds))
    if seconds < 60:
        return f"{seconds}s"
    
    minutes = seconds // 60
    rem_seconds = seconds % 60
    
    if minutes < 60:
        if rem_seconds == 0:
            return f"{minutes}m"
        return f"{minutes}m {rem_seconds:02d}s"
    
    hours = minutes // 60
    rem_minutes = minutes % 60
    if rem_seconds == 0:
        return f"{hours}h {rem_minutes}m"
    return f"{hours}h {rem_minutes}m {rem_seconds:02d}s"

def compute_sla_metrics(delays_seconds: List[float], target_seconds: int = 300) -> Dict[str, Any]:
    """Computes comprehensive SLA metrics across a list of detection delays."""
    if not delays_seconds:
        return {
            "total_articles": 0,
            "with_delay_data": 0,
            "avg_delay_seconds": 0,
            "avg_delay_formatted": "N/A",
            "fastest_delay_seconds": 0,
            "fastest_delay_formatted": "N/A",
            "slowest_delay_seconds": 0,
            "slowest_delay_formatted": "N/A",
            "within_sla_count": 0,
            "over_sla_count": 0,
            "within_sla_percent": 100.0,
            "over_sla_percent": 0.0,
        }

    valid_delays = [d for d in delays_seconds if d is not None and d >= 0]
    if not valid_delays:
        return {
            "total_articles": len(delays_seconds),
            "with_delay_data": 0,
            "avg_delay_seconds": 0,
            "avg_delay_formatted": "N/A",
            "fastest_delay_seconds": 0,
            "fastest_delay_formatted": "N/A",
            "slowest_delay_seconds": 0,
            "slowest_delay_formatted": "N/A",
            "within_sla_count": 0,
            "over_sla_count": 0,
            "within_sla_percent": 100.0,
            "over_sla_percent": 0.0,
        }

    avg_sec = sum(valid_delays) / len(valid_delays)
    fastest_sec = min(valid_delays)
    slowest_sec = max(valid_delays)
    within_sla = [d for d in valid_delays if d <= target_seconds]
    over_sla = [d for d in valid_delays if d > target_seconds]

    within_pct = round((len(within_sla) / len(valid_delays)) * 100, 1)
    over_pct = round((len(over_sla) / len(valid_delays)) * 100, 1)

    return {
        "total_articles": len(delays_seconds),
        "with_delay_data": len(valid_delays),
        "avg_delay_seconds": round(avg_sec, 2),
        "avg_delay_formatted": format_delay(avg_sec),
        "fastest_delay_seconds": round(fastest_sec, 2),
        "fastest_delay_formatted": format_delay(fastest_sec),
        "slowest_delay_seconds": round(slowest_sec, 2),
        "slowest_delay_formatted": format_delay(slowest_sec),
        "within_sla_count": len(within_sla),
        "over_sla_count": len(over_sla),
        "within_sla_percent": within_pct,
        "over_sla_percent": over_pct,
    }
