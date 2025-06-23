from utils.db_util import get_db_connection

def get_owner_by_yacht_id(yacht_id: str):
    """
    Fetches a list of (owner_name, owner_email, owner_number) for a given yacht_id.
    Returns a list of dicts.
    """
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT owner_name, owner_email, owner_number "
            "FROM yacht_owners WHERE yacht_id = %s",
            (yacht_id,)
        )
        rows = cursor.fetchall()
        # print(rows)
    
        if not rows:
            return {}
        
        owner_data = {}

        for row in rows:
            if row:
                name = row["owner_name"]
                email = row["owner_email"]
                number = row["owner_number"]

                if name not in owner_data:
                    owner_data[name] = {
                        "owner_name": name,
                        "owner_emails": [],
                        "owner_number": ""
                    }

                if email and email not in owner_data[name]["owner_emails"]:
                    owner_data[name]["owner_emails"].append(email)

                if not owner_data[name]["owner_number"] and number:
                    owner_data[name]["owner_number"] = number

        owners = list(owner_data.values())
        return owners

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
