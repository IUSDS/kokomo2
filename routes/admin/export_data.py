from fastapi import APIRouter, HTTPException
import pymysql
import pandas as pd
from io import StringIO
from utils.database import db_config

export_data_route = APIRouter()

# Function to export data as CSV
def export_data(table_name):
    try:
        conn = pymysql.connect(**db_config)
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql(query, conn)
        conn.close()
        
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)
        return csv_buffer.getvalue()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@export_data_route.post("/export/members")
def export_members():
    """Exports members table data as CSV"""
    csv_data = export_data("Members")
    return {"filename": "members.csv", "csv_data": csv_data}

@export_data_route.post("/export/visitors")
def export_visitors():
    """Exports visitors table data as CSV"""
    csv_data = export_data("Visitors")
    return {"filename": "visitors.csv", "csv_data": csv_data}