# fn_01_import_dataset.py

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

DATA_DIR = Path("dataset_download")

FILE_PATH = DATA_DIR / "sample_-_superstore.xls"

CHUNK_SIZE = 1000


# ============================================================
# DOWNLOAD DATASET
# ============================================================

def fn_download_dataset():

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Check if file already exists
    # --------------------------------------------------------

    if FILE_PATH.exists():

        print("Excel dataset already exists.")
        print(f"Using local file: {FILE_PATH}")

        return FILE_PATH

    # --------------------------------------------------------
    # Download file
    # --------------------------------------------------------

    print("Excel dataset not found.")
    print("Downloading Excel dataset...")
    print(f"URL: {FILE_URL}")

    response = requests.get(
        FILE_URL,
        timeout=60
    )

    response.raise_for_status()

    # Check response
    content_type = response.headers.get(
        "Content-Type",
        ""
    ).lower()

    if "text/html" in content_type:

        raise RuntimeError(
            "The download URL returned an HTML page "
            "instead of an Excel file."
        )

    # Save file
    with open(FILE_PATH, "wb") as file:

        file.write(response.content)

    print(
        f"Excel dataset downloaded: {FILE_PATH}"
    )

    return FILE_PATH


# ============================================================
# READ EXCEL DATASET
# ============================================================

def fn_read_dataset(file_path):

    print()
    print("Reading Excel worksheets...")

    excel_file = pd.ExcelFile(file_path)

    print(
        f"Worksheets found: "
        f"{excel_file.sheet_names}"
    )

    # Expected worksheets
    required_sheets = [
        "Orders",
        "People",
        "Returns"
    ]

    # Validate worksheets
    for sheet_name in required_sheets:

        if sheet_name not in excel_file.sheet_names:

            raise RuntimeError(
                f"Worksheet '{sheet_name}' "
                f"was not found."
            )

    # Read worksheets
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

    print(
        f"Orders  : {len(df_orders):,} rows"
    )

    print(
        f"People  : {len(df_people):,} rows"
    )

    print(
        f"Returns : {len(df_returns):,} rows"
    )

    return (
        df_orders,
        df_people,
        df_returns
    )


# ============================================================
# CREATE DATABASE TABLES
# ============================================================

def fn_create_tables(engine):

    print()
    print("Dropping existing tables...")

    with engine.begin() as connection:

        connection.execute(
            text("""
                DROP TABLE IF EXISTS returns;
                DROP TABLE IF EXISTS people;
                DROP TABLE IF EXISTS orders;
            """)
        )

    print("Existing tables dropped.")

    print()
    print("Creating tables...")

    with engine.begin() as connection:

        connection.execute(
            text("""
                CREATE TABLE orders (
                    "Row ID" INTEGER,
                    "Order ID" VARCHAR(50),
                    "Order Date" DATE,
                    "Ship Date" DATE,
                    "Ship Mode" VARCHAR(50),
                    "Customer ID" VARCHAR(50),
                    "Customer Name" VARCHAR(255),
                    "Segment" VARCHAR(50),
                    "Country/Region" VARCHAR(100),
                    "City" VARCHAR(100),
                    "State/Province" VARCHAR(100),
                    "Postal Code" VARCHAR(20),
                    "Region" VARCHAR(50),
                    "Product ID" VARCHAR(50),
                    "Category" VARCHAR(100),
                    "Sub-Category" VARCHAR(100),
                    "Product Name" TEXT,
                    "Sales" NUMERIC(18, 4),
                    "Quantity" INTEGER,
                    "Discount" NUMERIC(10, 4),
                    "Profit" NUMERIC(18, 4)
                );

                CREATE TABLE people (
                    "Regional Manager" VARCHAR(255),
                    "Region" VARCHAR(50)
                );

                CREATE TABLE returns (
                    "Order ID" VARCHAR(50),
                    "Returned" VARCHAR(20)
                );
            """)
        )

    print("Tables created successfully.")


# ============================================================
# INSERT DATAFRAME WITH PROGRESS
# ============================================================

def fn_insert_dataframe(
    df,
    table_name,
    engine,
    chunk_size=CHUNK_SIZE
):

    total_rows = len(df)

    print(
        f"Uploading '{table_name}' "
        f"({total_rows:,} rows)..."
    )

    if total_rows == 0:

        print(
            f"'{table_name}' contains no rows."
        )

        return

    # --------------------------------------------------------
    # Upload in chunks
    # --------------------------------------------------------

    for start in range(
        0,
        total_rows,
        chunk_size
    ):

        end = min(
            start + chunk_size,
            total_rows
        )

        df_chunk = df.iloc[start:end]

        df_chunk.to_sql(
            table_name,
            engine,
            if_exists="append",
            index=False,
            method="multi"
        )

        percentage = (
            end / total_rows
        ) * 100

        print(
            f"  {end:,} / {total_rows:,} rows "
            f"({percentage:.1f}%)"
        )


# ============================================================
# IMPORT DATASET
# ============================================================

def fn_import_dataset():

    print()
    print("=" * 60)
    print("SUPERSTORE DATA IMPORT")
    print("=" * 60)

    # --------------------------------------------------------
    # 1. Download dataset
    # --------------------------------------------------------

    print()
    print("[1/5] Checking Excel dataset...")

    file_path = fn_download_dataset()

    # --------------------------------------------------------
    # 2. Read dataset
    # --------------------------------------------------------

    print()
    print("[2/5] Reading dataset...")

    (
        df_orders,
        df_people,
        df_returns
    ) = fn_read_dataset(file_path)

    # --------------------------------------------------------
    # 3. Connect to PostgreSQL
    # --------------------------------------------------------

    print()
    print("[3/5] Connecting to PostgreSQL...")

    engine = fn_db_engine()

    try:

        # Test connection
        with engine.connect() as connection:

            connection.execute(
                text("SELECT 1")
            )

        print(
            "PostgreSQL connection successful."
        )

        # ----------------------------------------------------
        # 4. Drop and create tables
        # ----------------------------------------------------

        print()
        print("[4/5] Preparing database tables...")

        fn_create_tables(engine)

        # ----------------------------------------------------
        # 5. Insert data
        # ----------------------------------------------------

        print()
        print("[5/5] Uploading data...")

        fn_insert_dataframe(
            df_orders,
            "orders",
            engine
        )

        print()

        fn_insert_dataframe(
            df_people,
            "people",
            engine
        )

        print()

        fn_insert_dataframe(
            df_returns,
            "returns",
            engine
        )

        # ----------------------------------------------------
        # Complete
        # ----------------------------------------------------

        print()
        print("=" * 60)
        print("IMPORT COMPLETED SUCCESSFULLY")
        print("=" * 60)

        print()
        print("Imported rows:")
        print(
            f"  orders  : {len(df_orders):,}"
        )
        print(
            f"  people  : {len(df_people):,}"
        )
        print(
            f"  returns : {len(df_returns):,}"
        )

    finally:

        engine.dispose()

        print()
        print("PostgreSQL connection closed.")

