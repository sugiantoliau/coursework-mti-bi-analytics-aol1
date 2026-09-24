# fn_04_data_load.py

from sqlalchemy import text
from fn_db_function import fn_db_engine


CHUNK_SIZE = 1000


# ==========================================================
# 1. DROP EXISTING DATA WAREHOUSE TABLES
# ==========================================================

def fn_drop_transformed_tables(engine):

    print()
    print("Dropping existing Data Warehouse tables...")

    with engine.begin() as connection:

        # Drop Fact tables first because they have Foreign Keys
        connection.execute(
            text("""
                DROP TABLE IF EXISTS "Fact_Returns";
                DROP TABLE IF EXISTS "Fact_Order_Detail";

                DROP TABLE IF EXISTS "Dim_Order_Header";
                DROP TABLE IF EXISTS "Dim_Shipping";
                DROP TABLE IF EXISTS "Dim_Customer";
                DROP TABLE IF EXISTS "Dim_Product";
                DROP TABLE IF EXISTS "Dim_Region";
                DROP TABLE IF EXISTS "Dim_Date";
            """)
        )

    print("Existing Data Warehouse tables dropped.")


# ==========================================================
# 2. CREATE DATA WAREHOUSE TABLES
# ==========================================================

def fn_create_transformed_tables(engine):

    print()
    print("Creating Data Warehouse tables...")

    with engine.begin() as connection:

        # ------------------------------------------------------
        # Dim_Date
        # ------------------------------------------------------

        connection.execute(
            text("""
                CREATE TABLE "Dim_Date" (
                    "Date ID" INTEGER PRIMARY KEY,
                    "Date" DATE,
                    "Day" INTEGER,
                    "Month" INTEGER,
                    "Year" INTEGER
                );
            """)
        )

        # ------------------------------------------------------
        # Dim_Region
        # ------------------------------------------------------

        connection.execute(
            text("""
                CREATE TABLE "Dim_Region" (
                    "Region ID" INTEGER PRIMARY KEY,
                    "Regional Manager" VARCHAR(255),
                    "Region" VARCHAR(50)
                );
            """)
        )

        # ------------------------------------------------------
        # Dim_Product
        # ------------------------------------------------------

        connection.execute(
            text("""
                CREATE TABLE "Dim_Product" (
                    "Product ID" VARCHAR(50) PRIMARY KEY,
                    "Category" VARCHAR(100),
                    "Sub-Category" VARCHAR(100),
                    "Product Name" TEXT
                );
            """)
        )

        # ------------------------------------------------------
        # Dim_Customer
        # ------------------------------------------------------

        connection.execute(
            text("""
                CREATE TABLE "Dim_Customer" (
                    "Customer ID" VARCHAR(50) PRIMARY KEY,
                    "Customer Name" VARCHAR(255),
                    "Segment" VARCHAR(50),
                    "Country" VARCHAR(100),
                    "City" VARCHAR(100),
                    "State/Province" VARCHAR(100),
                    "Postal Code" VARCHAR(20)
                );
            """)
        )

        # ------------------------------------------------------
        # Dim_Shipping
        # ------------------------------------------------------

        connection.execute(
            text("""
                CREATE TABLE "Dim_Shipping" (
                    "Ship ID" INTEGER PRIMARY KEY,
                    "Ship Mode" VARCHAR(50)
                );
            """)
        )

        # ------------------------------------------------------
        # Dim_Order_Header
        # ------------------------------------------------------

        connection.execute(
            text("""
                CREATE TABLE "Dim_Order_Header" (
                    "Order ID" VARCHAR(50) PRIMARY KEY,
                    "Date ID" INTEGER,
                    "Order Date" DATE,
                    "Ship Date" DATE,
                    "Ship ID" INTEGER,
                    "Customer ID" VARCHAR(50),
                    "Region ID" INTEGER,

                    CONSTRAINT fk_order_header_date
                        FOREIGN KEY ("Date ID")
                        REFERENCES "Dim_Date" ("Date ID"),

                    CONSTRAINT fk_order_header_shipping
                        FOREIGN KEY ("Ship ID")
                        REFERENCES "Dim_Shipping" ("Ship ID"),

                    CONSTRAINT fk_order_header_customer
                        FOREIGN KEY ("Customer ID")
                        REFERENCES "Dim_Customer" ("Customer ID"),

                    CONSTRAINT fk_order_header_region
                        FOREIGN KEY ("Region ID")
                        REFERENCES "Dim_Region" ("Region ID")
                );
            """)
        )

        # ------------------------------------------------------
        # Fact_Order_Detail
        # ------------------------------------------------------

        connection.execute(
            text("""
                CREATE TABLE "Fact_Order_Detail" (
                    "Order ID" VARCHAR(50),
                    "Product ID" VARCHAR(50),
                    "Sales" NUMERIC(18, 4),
                    "Quantity" INTEGER,
                    "Discount" NUMERIC(10, 4),
                    "Profit" NUMERIC(18, 4),

                    CONSTRAINT fk_order_detail_order
                        FOREIGN KEY ("Order ID")
                        REFERENCES "Dim_Order_Header" ("Order ID"),

                    CONSTRAINT fk_order_detail_product
                        FOREIGN KEY ("Product ID")
                        REFERENCES "Dim_Product" ("Product ID")
                );
            """)
        )

        # ------------------------------------------------------
        # Fact_Returns
        # ------------------------------------------------------

        connection.execute(
            text("""
                CREATE TABLE "Fact_Returns" (
                    "Order ID" VARCHAR(50) PRIMARY KEY,
                    "Returned" VARCHAR(20),
                    "Return_Count" INTEGER,

                    CONSTRAINT fk_returns_order
                        FOREIGN KEY ("Order ID")
                        REFERENCES "Dim_Order_Header" ("Order ID")
                );
            """)
        )

    print("Data Warehouse tables created successfully.")


# ==========================================================
# 3. LOAD DATAFRAME INTO POSTGRESQL
# ==========================================================

def fn_load_dataframe(
    df,
    table_name,
    engine
):

    total_rows = len(df)

    print()
    print(
        f"Loading {table_name} "
        f"({total_rows:,} rows)..."
    )

    if total_rows == 0:

        print(
            f"{table_name} contains no rows."
        )

        return

    for start in range(
        0,
        total_rows,
        CHUNK_SIZE
    ):

        end = min(
            start + CHUNK_SIZE,
            total_rows
        )

        print(
            f"  Preparing rows "
            f"{start + 1:,}-{end:,} "
            f"of {total_rows:,}..."
        )

        df_chunk = df.iloc[start:end]

        print(
            f"  Uploading rows "
            f"{start + 1:,}-{end:,}..."
        )

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
            f"  Completed: "
            f"{end:,} / {total_rows:,} "
            f"({percentage:.1f}%)"
        )

    print(
        f"{table_name} loaded successfully."
    )


# ==========================================================
# 4. CHECK LOADED ROW COUNTS
# ==========================================================

def fn_check_load_results(
    engine
):

    print()
    print("=" * 60)
    print("LOAD RESULTS")
    print("=" * 60)

    table_names = [
        "Dim_Date",
        "Dim_Region",
        "Dim_Product",
        "Dim_Customer",
        "Dim_Shipping",
        "Dim_Order_Header",
        "Fact_Order_Detail",
        "Fact_Returns"
    ]

    with engine.connect() as connection:

        for table_name in table_names:

            result = connection.execute(
                text(
                    f'''
                    SELECT COUNT(*)
                    FROM "{table_name}"
                    '''
                )
            )

            row_count = result.scalar()

            print(
                f"  {table_name:<20}: "
                f"{row_count:,} rows"
            )

    print()
    print("Load result verification completed.")


# ==========================================================
# 5. MAIN DATA LOAD FUNCTION
# ==========================================================

def fn_data_load(
    df_dim_date,
    df_dim_region,
    df_dim_product,
    df_dim_customer,
    df_dim_shipping,
    df_dim_order_header,
    df_fact_order_detail,
    df_fact_returns
):

    print()
    print("=" * 60)
    print("DATA LOAD")
    print("=" * 60)

    engine = fn_db_engine()

    try:

        # ------------------------------------------------------
        # Full Load
        # ------------------------------------------------------

        fn_drop_transformed_tables(
            engine
        )

        fn_create_transformed_tables(
            engine
        )

        print()
        print(
            "Loading transformed data "
            "into PostgreSQL..."
        )

        # ------------------------------------------------------
        # Load Dimension Tables First
        # ------------------------------------------------------

        print()
        print("-" * 60)
        print("LOADING DIMENSION TABLES")
        print("-" * 60)

        fn_load_dataframe(
            df_dim_date,
            "Dim_Date",
            engine
        )

        fn_load_dataframe(
            df_dim_region,
            "Dim_Region",
            engine
        )

        fn_load_dataframe(
            df_dim_product,
            "Dim_Product",
            engine
        )

        fn_load_dataframe(
            df_dim_customer,
            "Dim_Customer",
            engine
        )

        fn_load_dataframe(
            df_dim_shipping,
            "Dim_Shipping",
            engine
        )

        fn_load_dataframe(
            df_dim_order_header,
            "Dim_Order_Header",
            engine
        )

        # ------------------------------------------------------
        # Load Fact Tables
        # ------------------------------------------------------

        print()
        print("-" * 60)
        print("LOADING FACT TABLES")
        print("-" * 60)

        fn_load_dataframe(
            df_fact_order_detail,
            "Fact_Order_Detail",
            engine
        )

        fn_load_dataframe(
            df_fact_returns,
            "Fact_Returns",
            engine
        )

        # ------------------------------------------------------
        # Check Load Results
        # ------------------------------------------------------

        fn_check_load_results(
            engine
        )

        print()
        print("=" * 60)
        print("DATA LOAD COMPLETED SUCCESSFULLY")
        print("=" * 60)

    finally:

        engine.dispose()

        print()
        print("PostgreSQL connection closed.")
