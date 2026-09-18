import pandas as pd
from fn_db_function import fn_db_engine


def fn_data_extract():
    print()
    print("=" * 60)
    print("DATA EXTRACT")
    print("=" * 60)

    engine = fn_db_engine()

    try:
        print()
        print("Extracting data from PostgreSQL...")

        df_orders = pd.read_sql(
            'SELECT * FROM orders',
            engine
        )

        df_people = pd.read_sql(
            'SELECT * FROM people',
            engine
        )

        df_returns = pd.read_sql(
            'SELECT * FROM returns',
            engine
        )

        print()
        print("Data extraction completed.")
        print(f"  orders  : {len(df_orders):,} rows")
        print(f"  people  : {len(df_people):,} rows")
        print(f"  returns : {len(df_returns):,} rows")

        return df_orders, df_people, df_returns

    finally:
        engine.dispose()
        print()
        print("PostgreSQL connection closed.")