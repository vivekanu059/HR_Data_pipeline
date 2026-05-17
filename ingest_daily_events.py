import json
import pyodbc
import os
from datetime import datetime


SERVER_NAME = r'localhost\SQLEXPRESS' 
DATABASE_NAME = 'EnterpriseHR'

conn_str = f'DRIVER={{SQL Server}};SERVER={SERVER_NAME};DATABASE={DATABASE_NAME};Trusted_Connection=yes;'

def load_daily_json(target_date_str):
    """Reads a specific day's JSON file and loads it into SQL Server."""
    
    file_path = rf"D:\hr_data_pipeline\data\raw_json\hr_events_{target_date_str}.json"
    
    if not os.path.exists(file_path):
        print(f"⚠️ No data file found for {target_date_str}. Skipping.")
        return

    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        print(f"✅ Connected to SQL Server database: {DATABASE_NAME}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return

    # 2. Read the JSON file
    with open(file_path, 'r') as file:
        daily_events = json.load(file)

    print(f"🔄 Processing {len(daily_events)} events for {target_date_str}...")

   
    insert_query = """
        INSERT INTO hr_staging.raw_daily_events 
        (event_id, event_timestamp, emp_id, event_type, new_salary, new_role, new_department, new_hire_details)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """

    inserted_count = 0
    for event in daily_events:
        # Extract values, defaulting to None (NULL in SQL) if they don't exist
        event_id = event['event_id']
        timestamp = event['timestamp']
        emp_id = event['emp_id']
        event_type = event['event_type']
        
        new_salary = event.get('new_salary')
        new_role = event.get('new_role')
        new_department = event.get('new_department')
        
        # If it's a new hire, convert the nested dictionary back to a JSON string for SQL
        new_hire_details = json.dumps(event['details']) if 'details' in event else None

        try:
            cursor.execute(insert_query, 
                           event_id, timestamp, emp_id, event_type, 
                           new_salary, new_role, new_department, new_hire_details)
            inserted_count += 1
        except Exception as e:
            print(f"⚠️ Failed to insert event {event_id}: {e}")

    # 4. Commit the transaction and close
    conn.commit()
    cursor.close()
    conn.close()
    print(f"🎉 Successfully loaded {inserted_count} events into hr_staging.raw_daily_events!")

    
if __name__ == "__main__":
    from datetime import datetime, timedelta
    
    # Start date matching your generation script
    start_date = datetime(2025, 1, 1) 
    
    # Loop through 365 days and ingest each file
    for i in range(365):
        target_date = (start_date + timedelta(days=i)).strftime('%Y-%m-%d')
        load_daily_json(target_date)