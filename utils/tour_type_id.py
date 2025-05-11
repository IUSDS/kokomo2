from typing import Optional
from utils.database import get_db_connection
import dateutil.parser

def normalize_yacht_name(raw: str) -> str:
    parts = raw.split(" - ")
    return parts[1].strip() if len(parts) > 1 else raw

def get_exact_half_day_tour_name(base_name: str, start_time_str: str) -> Optional[str]:
    if base_name != "Half Day":
        return None

    start_time = dateutil.parser.isoparse(start_time_str)
    return "Half Day Morning Tour" if start_time.hour < 12 else "Half Day Afternoon Tour"

def get_tour_id_by_name(name: str, start_time_str: str) -> Optional[str]:
    conn = None
    cursor = None

    base_name = normalize_yacht_name(name)
    print("base name:", base_name)

    if base_name == "Half Day":
        mapped_name = get_exact_half_day_tour_name(base_name, start_time_str)
    else:
        mapped_name = {
            "Sunset": "Sunset Tour",
            "Full Day": "1 Full Day",
        }.get(base_name)

    if not mapped_name:
        print("No mapped tour name found for:", name)
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
