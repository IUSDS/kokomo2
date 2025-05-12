from typing import Optional
from utils.db_util import get_db_connection
import dateutil.parser

def get_exact_half_day_tour_name(start_time_str: str) -> str:
    """
    Determines whether the tour is morning or afternoon based on start time.
    """
    start_time = dateutil.parser.isoparse(start_time_str)
    return "Half Day Morning Tour" if start_time.hour < 12 else "Half Day Afternoon Tour"

def map_webhook_tour_name(webhook_name: str, start_time_str: str) -> Optional[str]:
    """
    Maps incoming webhook tour name to the tour_types.name in DB.
    """
    name = webhook_name.strip().upper()

    if "HALF DAY" in name:
        return get_exact_half_day_tour_name(start_time_str)
    elif "FULL DAY" in name:
        return "1 Full Day"
    elif "SUNSET" in name:
        return "Sunset Tour"
    else:
        return None

def get_tour_id_by_name(webhook_name: str, start_time_str: str) -> Optional[str]:
    conn = None
    cursor = None

    mapped_name = map_webhook_tour_name(webhook_name, start_time_str)
    print("Mapped tour name:", mapped_name)

    if not mapped_name:
        print("No mapped tour name found for:", webhook_name)
        return None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM tour_types WHERE name = %s LIMIT 1",
            (mapped_name,)
        )
        row = cursor.fetchone()
        return row['id'] if row else None

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
