from sqlalchemy import text
from fn_db_function import fn_db_engine

CHUNK_SIZE = 1000


def fn_drop_transformed_tables(engine):
    print()
    print("Dropping existing transformed tables...")

    with engine.begin() as connection:
        connection.execute(
            text("""
                DROP TABLE IF EXISTS returns_transformed;
                DROP TABLE IF EXISTS people_transformed;
                DROP TABLE IF EXISTS orders_transformed;
            """)
        )

    print("Existing transformed tables dropped.")


def fn_load_dataframe(df, table_name, engine):
    total_rows = len(df)

    print()
    print(
        f"Loading {table_name} "
        f"({total_rows:,} rows)..."
    )

    if total_rows == 0:
        print(f"{table_name} contains no rows.")
        return

    for start in range(0, total_rows, CHUNK_SIZE):

        end = min(start + CHUNK_SIZE, total_rows)

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

        percentage = (end / total_rows) * 100

        print(
            f"  Completed: "
            f"{end:,} / {total_rows:,} "
            f"({percentage:.1f}%)"
        )

    print(
        f"{table_name} loaded successfully."
    )


def fn_data_load(
    df_orders,
    df_people,
    df_returns
):
    print()
    print("=" * 60)
    print("DATA LOAD")
    print("=" * 60)

    engine = fn_db_engine()

    try:
        fn_drop_transformed_tables(engine)

        print()
        print("Loading transformed data into PostgreSQL...")

        fn_load_dataframe(
            df_orders,
            "orders_transformed",
            engine
        )

        fn_load_dataframe(
            df_people,
            "people_transformed",
            engine
        )

        fn_load_dataframe(
            df_returns,
            "returns_transformed",
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