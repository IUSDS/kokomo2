from typing import Optional
from utils.db_util import get_db_connection

# Mapping webhook names to actual DB yacht names
WEBHOOK_YACHT_MAP = {
    "KYC - Wanderlust": "Wanderlust", 
    "KYC- 43' - Giddy Up": "Giddy Up",
    "KYC - Top Shelf": "Top Shelf",
    "KYC - 35' Ocean Rode- Half Day Outing": "Ocean Rode",
    "KYC - The Life - 29' - Up to 6 People -OSPREY pickup": "The Life",
    "KYC - 42' Outrage - Anna Maria Half Day Outing": "Outrage",
    "KYC - 50' Lil' Bit Nauti - Bradenton": "Lil' Bit Nauti",
    "KYC - Memories Not Dreams": "Memories Not Dreams",
    "KYC - Congetta - The Vinoy in St. Pete": "Congetta",
    "KYC- 40' Aviara - Thirst Trap": "Thirst Trap",
    "KYC - 63' Prestige - Peace - Reservation": "Peace",
    "KYC - Memory Maker" : "Memory Maker",
    "KYC- 40' Happy Hour" : "Happy Hour",
    "KYC- 40' Golden Ticket" : "Golden Ticket",
}

ALL_YACHT_NAMES = {
    "KYC - Wanderlust": "Wanderlust", 
    "KYC- 43' - Giddy Up": "Giddy Up",
    "KYC - Top Shelf": "Top Shelf",
    "KYC - 35' Ocean Rode- Half Day Outing": "Ocean Rode",
    "KYC - The Life - 29' - Up to 6 People -OSPREY pickup": "The Life",
    "KYC - 42' Outrage - Anna Maria Half Day Outing": "Outrage",
    "KYC - 50' Lil' Bit Nauti - Bradenton": "Lil' Bit Nauti",
    "KYC - Memories Not Dreams": "Memories Not Dreams",
    "KYC - Congetta - The Vinoy in St. Pete": "Congetta",
    "KYC- 40' Aviara - Thirst Trap": "Thirst Trap",
    "KYC - 63' Prestige - Peace - Reservation": "Peace",
    "KYC - Memory Maker" : "Memory Maker",
    "KYC- 40' Happy Hour" : "Happy Hour",
    "KYC- 40' Golden Ticket" : "Golden Ticket",
    
    "42' \"Wanderlust\" Sailing Catamaran - Full Day Charter": "Wanderlust",
    "42' \"Wanderlust\" Sailing Catamaran - Half Day Sail": "Wanderlust",
    "42' \"Wanderlust\" Sailing Catamaran - 3 Hour Special": "Wanderlust",
    "42' \"Wanderlust\" Sunset Sail": "Wanderlust",
    "Wanderlust -Sailing Catamaran - Sleeps 8": "Wanderlust",
    
    "43' \"Giddy Up!\" - Full Day Charter": "Giddy Up",
    "43' \"Giddy Up!\" - Half Day - 4 Hour Charter": "Giddy Up",
    "43' \"Giddy Up!\" - 3 Hour Charter": "Giddy Up",
    "43' \"Giddy Up!\" - Sunset Cruise": "Giddy Up",
    "Giddy Up - 2 Hour Dolphin Tour": "Giddy Up",
    
    "Top Shelf: Full Day Charter": "Top Shelf",
    "Top Shelf: 6 Hour Charter": "Top Shelf",
    "Top Shelf: Half Day Charter": "Top Shelf",
    "Top Shelf: 3 Hour Daytime Charter": "Top Shelf",
    "Top Shelf: Sunset Charter": "Top Shelf",
    "Top Shelf: 2 Hour Dolphin Cruise": "Top Shelf",
    
    "35' Ocean Rode - 6 & 8 Hour Private Luxury Charter": "Ocean Rode",
    "35' Ocean Rode- Half Day Private Luxury Charter": "Ocean Rode",
    "35' Ocean Rode- Sunset Private Luxury Charter": "Ocean Rode",
    
    "Lil' Bit Nauti! : Half Day Charter - Anna Maria": "Lil' Bit Nauti",
    "Lil' Bit Nauti! : 3-4 Hour Sunset Charter - Anna Maria": "Lil' Bit Nauti",
    "Lil' Bit Nauti! : 6-8 Hour Charter - Anna Maria Island": "Lil' Bit Nauti",
    
    "50’ Memories Not Dreams - Tampa": "Memories Not Dreams",
    "50’ Memories Not Dreams - Full Day Charter - St. Pete": "Memories Not Dreams",
    "50’ Memories Not Dreams - Half Day Charter": "Memories Not Dreams",
    "50’ Memories Not Dreams - 3 Hour Daytime Cruise": "Memories Not Dreams",
    "50’ Memories Not Dreams - Sunset Charter": "Memories Not Dreams",
    
    "Full Day Private Charter - Downtown St. Pete": "Congetta",
    "Half Day Private Charter - Downtown St. Pete": "Congetta",
    "Sunset Private Charter - Downtown St. Pete": "Congetta",
    "Full Day Private Charter - Downtown Tampa Bay": "Congetta",
    "Half Day Private Charter - Downtown Tampa Bay": "Congetta",
    "Sunset Private Charter - Downtown Tampa Bay": "Congetta",
    
    "40' Thirst - Half Day Charter - Venice": "Thirst Trap",
    "40' Thirst- Sunset Charter - Venice": "Thirst Trap",
    "40' Thirst- Full Day 6- 8 Hour Charter - Venice": "Thirst Trap",
    
    "63' Prestige - Peace - Full Day Outing": "Peace",
    "63' Prestige - Peace - Half Day Outing": "Peace",
    "63' Prestige - Peace - Sunset Outing": "Peace",
    
    "Memory Maker: Full Day Charters" : "Memory Maker",
    "Memory Maker: Half Day Charter" : "Memory Maker",
    "Memory Maker: 3 Hour Cruise" : "Memory Maker",
    "Memory Maker: Sunset Charter" : "Memory Maker",
    "Memory Maker: Multi-Day Charters - Sleeps 6" : "Memory Maker",
    
    "40' Happy Hour - 6 & 8 Hour Full Day Charter" : "Happy Hour",
    "40' Happy Hour - Half Day Charter" : "Happy Hour",
    "40' Happy Hour - 3 and 4 Hour Sunset Charter" : "Happy Hour",
    
    "40' \"Golden Ticket\" - Half Day - 4 Hour Charter" : "Golden Ticket",
    "40' \"Golden Ticket\" - 6 & 8 Hour Full Day Charter" : "Golden Ticket",
    "40' \"Golden Ticket\" - Sunset Charter" : "Golden Ticket",
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
            
def get_mapped_yacht_name_for_invite(webhook_name: str) -> str:
    cleaned = webhook_name.strip()
    return ALL_YACHT_NAMES.get(cleaned, cleaned)
            
def get_yacht_id_for_invite(name: str) -> Optional[str]:
    conn = None
    cursor = None

    base_name = get_mapped_yacht_name_for_invite(name)
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
