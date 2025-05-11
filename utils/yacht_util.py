from typing import Optional
from utils.db_util import get_db_connection

# Mapping webhook names to actual DB yacht names
WEBHOOK_YACHT_MAP = {
    "KYC - Wanderlust": "Wanderlust", 
    "KYC- 43' - Giddy Up": "Giddy Up",
    "KYC - Top Shelf": "Top Shelf",
    "KYC - 35' Ocean Rode- Half Day Outing": "Aviara",
    "KYC - The Life - 29' - Up to 6 People -OSPREY pickup": "The Life",
    "KYC - 42' Outrage - Anna Maria Half Day Outing": "Outrage",
    "KYC - 50' Lil' Bit Nauti - Bradenton": "Lil' Bit Nauti",
    "KYC - Memories Not Dreams": "Memories Not Dreams",
    "KYC - Congetta - The Vinoy in St. Pete": "Congetta",
    "KYC- 40' Aviara - Thirst Trap": "Thirst Trap",
    "KYC- 63' Prestige - Peace - Reservation": "Peace",
    "": "Tiara Fly"  # Last empty key wins if duplicate empty strings exist
}

def get_mapped_yacht_name(webhook_name: str) -> str:
    cleaned = webhook_name.strip()
    return WEBHOOK_YACHT_MAP.get(cleaned, cleaned)

def get_yacht_id_by_name(name: str) -> Optional[str]:
    conn = None
    cursor = None

    base_name = get_mapped_yacht_name(name)
    print("base name:", base_name)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM yachts WHERE name = %s LIMIT 1",
            (base_name,)
        )
        row = cursor.fetchone()
        return row['id'] if row else None

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
