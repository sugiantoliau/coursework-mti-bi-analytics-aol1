```python
from pathlib import Path

import pandas as pd
import requests
from sqlalchemy import text

from fn_db_function import fn_db_engine


# ============================================================
# CONFIGURATION
# ============================================================

FILE_URL = (
    "https://public.tableau.com/app/sample-data/"
    "sample_-_superstore.xls"
)

DATA_DIR = Path("data")
FILE_PATH = DATA_DIR / "sample_-_superstore.xls"


# ============================================================
# DOWNLOAD EXCEL IF FILE DOES NOT EXIST
# ============================================================

def download_excel():

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    if FILE_PATH.exists():

        print("Excel dataset already exists.")
        print(f"Using local file: {FILE_PATH}")

        return FILE_PATH

    print("Excel dataset not found.")
    print("Downloading Excel dataset...")
    print(f"URL: {FILE_URL}")

    response = requests.get(
        FILE_URL,
        timeout=60
    )

    response.raise_for_status()

    with open(FILE_PATH, "wb") as file:
        file.write(response.content)

    print(f"Excel dataset downloaded: {FILE_PATH}")

    return FILE_PATH


# ============================================================
# READ EXCEL WORKSHEETS
# ============================================================

def read_excel(file_path):

    print("Reading all worksheets...")

    excel_file = pd.ExcelFile(file_path)

    print(f"Worksheets: {excel_file.sheet_names}")

    df_orders = pd.read_excel(
        excel_file,
        sheet_name="Orders"
    )

    df_people = pd.read_excel(
        excel_file,
        sheet_name="People"
    )

    df_returns = pd.read_excel(
        excel_file,
        sheet_name="Returns"
    )

    return (
        df_orders,
        df_people,
        df_returns
    )


# ============================================================
# DROP AND CREATE TABLES
# ============================================================

def create_tables(engine):

    print("Dropping existing tables...")

    with engine.begin() as connection:

        connection.execute(
```
