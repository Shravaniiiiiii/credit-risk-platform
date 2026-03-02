import snowflake.connector
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()

def get_connection():
    return snowflake.connector.connect(
        
        user=os.getenv('SNOWFLAKE_USER'),
        password=os.getenv('SNOWFLAKE_PASSWORD'),
        account=os.getenv('SNOWFLAKE_ACCOUNT'),
        database='CREDIT_RISK_DB',
        schema='ANALYTICS',
        warehouse='ANALYTICS_WH'
    )

def load_csv_to_snowflake(csv_path, table_name):
    print(f'Loading {csv_path} into {table_name}...')
    df = pd.read_csv(csv_path)
    df.columns = [c.upper() for c in df.columns]  # Snowflake prefers uppercase

    conn = get_connection()
    cursor = conn.cursor()

    # Auto-create table from DataFrame schema
    from snowflake.connector.pandas_tools import write_pandas
    success, nchunks, nrows, _ = write_pandas(
        conn, df, table_name, auto_create_table=True, overwrite=True
    )
    print(f'Loaded {nrows:,} rows into {table_name}')
    conn.close()

if __name__ == '__main__':
    load_csv_to_snowflake('data/raw/application_train.csv', 'APPLICATIONS')
    load_csv_to_snowflake('data/raw/bureau.csv', 'BUREAU')
    load_csv_to_snowflake('data/raw/train_transaction.csv', 'TRANSACTIONS')
