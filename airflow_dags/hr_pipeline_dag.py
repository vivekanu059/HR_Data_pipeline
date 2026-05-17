from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pyodbc


SERVER_NAME = r'localhost\SQLEXPRESS'
DATABASE_NAME = 'EnterpriseHR'


def execute_scd_stored_procedure():
    """Connects to SQL Server and triggers the SCD Type 2 logic."""
    conn_str = f'DRIVER={{SQL Server}};SERVER={SERVER_NAME};DATABASE={DATABASE_NAME};Trusted_Connection=yes;'
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        print("Connected to SQL Server. Executing Stored Procedure...")
        
        cursor.execute("EXEC hr_analytics.sp_process_daily_events;")
        conn.commit()
        
        print("Stored Procedure executed successfully.")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error executing procedure: {e}")
        raise e # Fail the Airflow task if this breaks

default_args = {
    'owner': 'data_engineering_team',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


with DAG(
    'enterprise_hr_etl_pipeline',
    default_args=default_args,
    description='End-to-end HR data pipeline with SCD Type 2 tracking',
    schedule_interval='@daily', 
    catchup=False
) as dag:

    generate_data = BashOperator(
        task_id='generate_daily_hr_events',
        bash_command='python D:/hr_data_pipeline/generate_hr_data.py' 
    )
    ingest_data = BashOperator(
        task_id='ingest_json_to_staging',
        bash_command='python D:/hr_data_pipeline/ingest_daily_events.py'
    )

   
    process_data_warehouse = PythonOperator(
        task_id='apply_scd_type_2_logic',
        python_callable=execute_scd_stored_procedure
    )


    generate_data >> ingest_data >> process_data_warehouse