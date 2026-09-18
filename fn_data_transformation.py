import pandas as pd


def fn_data_transformation(
    df_orders,
    df_people,
    df_returns
):
    print()
    print("=" * 60)
    print("DATA TRANSFORMATION")
    print("=" * 60)

    df_orders = df_orders.copy()
    df_people = df_people.copy()
    df_returns = df_returns.copy()

    print()
    print("Transforming Orders data...")

    df_orders["Order Date"] = pd.to_datetime(
        df_orders["Order Date"],
        errors="coerce"
    )

    df_orders["Ship Date"] = pd.to_datetime(
        df_orders["Ship Date"],
        errors="coerce"
    )

    df_orders["Sales"] = pd.to_numeric(
        df_orders["Sales"],
        errors="coerce"
    )

    df_orders["Quantity"] = pd.to_numeric(
        df_orders["Quantity"],
        errors="coerce"
    )

    df_orders["Discount"] = pd.to_numeric(
        df_orders["Discount"],
        errors="coerce"
    )

    df_orders["Profit"] = pd.to_numeric(
        df_orders["Profit"],
        errors="coerce"
    )

    print("Orders transformation completed.")

    print()
    print("Transformation completed.")
    print(f"  orders  : {len(df_orders):,} rows")
    print(f"  people  : {len(df_people):,} rows")
    print(f"  returns : {len(df_returns):,} rows")

    return df_orders, df_people, df_returns