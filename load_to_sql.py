import pandas as pd
from sqlalchemy import create_engine
import os

try:
    # STEP 1: DB CONNECTION
    engine = create_engine(
        "postgresql+psycopg2://postgres:Logesh%401234@localhost:5432/postgres"
    )

    conn = engine.connect()
    print("✅ Connected to PostgreSQL")

    # STEP 2: BASE DIRECTORY
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # STEP 3: FILE MAPPING
    files = {
        "volatility_summary": "ticker_csv_files/volatility_summary.csv",
        "risk_return": "ticker_csv_files/risk_return.csv",
        "top_gainers": "ticker_csv_files/top_gainers.csv",
        "top_losers": "ticker_csv_files/top_losers.csv",
        "monthly_returns": "ticker_csv_files/monthly_returns.csv",
        "sector_performance": "ticker_csv_files/sector_performance.csv",
        "cumulative_return": "ticker_csv_files/Cumulative_Return_Over_Time.csv",
        "correlation_matrix": "ticker_csv_files/correlation_matrix.csv"
    }

    # STEP 4: LOAD DATA
    for table_name, relative_path in files.items():

        file_path = os.path.join(BASE_DIR, relative_path)

        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            continue

        df = pd.read_csv(file_path)

        df.to_sql(table_name, engine, if_exists="replace", index=False)

        print(f"✅ Loaded table: {table_name}")

    print("\n All data loaded successfully!")

    conn.close()

except Exception as e:
    print("FULL ERROR:")
    print(e)