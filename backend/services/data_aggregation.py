import os
import psycopg2
from psycopg2 import sql
import requests
from fastapi import HTTPException

DATABASE_URL = os.getenv("DATABASE_URL")

def get_health_data(source_url):
    try:
        response = requests.get(source_url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data from {source_url}: {str(e)}")

def aggregate_health_data(sources):
    aggregated_data = []
    for source in sources:
        data = get_health_data(source)
        aggregated_data.extend(data.get("results", []))
    return aggregated_data

def store_data_in_db(data):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        insert_query = sql.SQL("INSERT INTO health_data (source, data) VALUES (%s, %s)")
        
        for item in data:
            cursor.execute(insert_query, (item.get("source"), item.get("data")))
        
        conn.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

def run_data_aggregation(sources):
    aggregated_data = aggregate_health_data(sources)
    if not aggregated_data:
        raise HTTPException(status_code=404, detail="No data aggregated")
    store_data_in_db(aggregated_data)