import re

def extract_int(value, default=0):
    """
    Extracts the first integer from a string like "6 People" or returns the integer if already one.
    Returns the default if no valid number is found.
    """
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        match = re.search(r'\d+', value)
        return int(match.group()) if match else default
    return default

def parse_booking_payload(booking: dict, member_id: int) -> dict:
    availability = booking.get("availability", {})
    custom_fields = booking.get("custom_field_values", [])

    def get_custom_value(name: str, default=None):
        for field in custom_fields:
            if field.get("name") == name:
                return field.get("display_value") or field.get("value") or default
        return default

    return {
        "member_id": member_id,
        "booking_id": booking.get("pk"),
        "dashboard_url": f"https://kokomoyachtclub.vip/dashboard/{booking.get('pk')}",
        "created_at": booking.get("created_at"),
        "start_at": availability.get("start_at"),
        "end_at": availability.get("end_at"),
        "vessel_name": booking.get("availability", {}).get("item", {}).get("name", "Unknown"),
        "tour_type": booking.get("availability", {}).get("headline", "Unknown"),
        "pickup_point": get_custom_value("Pick Up Locations - KYC", ""),
        "invoice_price_display": booking.get("invoice_price_display"),
        "amount_paid_display": booking.get("amount_paid_display"),
        "receipt_subtotal_display": booking.get("receipt_subtotal_display"),
        "receipt_taxes_display": booking.get("receipt_taxes_display"),
        "receipt_total_display": booking.get("receipt_total_display"),
        "other_add_ons": get_custom_value("Additional Add Ons - flowers, music, etc", "No"),
        "adult_beverages": get_custom_value("Adult Beverages", "No"),
        "catering_option": get_custom_value("Catering Option?", "No"),
        "number_of_adults": extract_int(get_custom_value("How many people are in your party? (no pricing)")),
        "number_of_kids": extract_int(get_custom_value("How many kids in your party are under 6?")),
        "e_foil_count": extract_int(get_custom_value("E-foil")),
        "sea_bob_count": extract_int(get_custom_value("Sea Bob")),
    }
