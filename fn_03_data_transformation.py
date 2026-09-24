# fn_03_data_transformation.py

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

    # ==========================================================
    # 1. COPY SOURCE DATA
    # ==========================================================

    df_orders = df_orders.copy()
    df_people = df_people.copy()
    df_returns = df_returns.copy()

    # ==========================================================
    # 2. CHANGE DATA FORMAT AND DATA TYPES
    # ==========================================================

    print()
    print("Transforming data types...")

    # Order Date -> Date
    df_orders["Order Date"] = pd.to_datetime(
        df_orders["Order Date"],
        errors="coerce"
    )

    # Ship Date -> Date
    df_orders["Ship Date"] = pd.to_datetime(
        df_orders["Ship Date"],
        errors="coerce"
    )

    # Sales -> Numeric
    df_orders["Sales"] = pd.to_numeric(
        df_orders["Sales"],
        errors="coerce"
    )

    # Quantity -> Numeric
    df_orders["Quantity"] = pd.to_numeric(
        df_orders["Quantity"],
        errors="coerce"
    )

    # Discount -> Numeric
    df_orders["Discount"] = pd.to_numeric(
        df_orders["Discount"],
        errors="coerce"
    )

    # Profit -> Numeric
    df_orders["Profit"] = pd.to_numeric(
        df_orders["Profit"],
        errors="coerce"
    )

    print("Data type transformation completed.")

    # ==========================================================
    # 3. CREATE DIM_DATE
    # ==========================================================

    print()
    print("Creating Dim_Date...")

    df_dim_date = (
        df_orders[
            ["Order Date"]
        ]
        .dropna()
        .drop_duplicates()
        .rename(
            columns={
                "Order Date": "Date"
            }
        )
        .sort_values(by="Date")
        .reset_index(drop=True)
    )

    # Create Date ID with YYYYMMDD format
    df_dim_date["Date ID"] = (
        df_dim_date["Date"]
        .dt.strftime("%Y%m%d")
        .astype(int)
    )

    # Create Day, Month, and Year
    df_dim_date["Day"] = df_dim_date["Date"].dt.day
    df_dim_date["Month"] = df_dim_date["Date"].dt.month
    df_dim_date["Year"] = df_dim_date["Date"].dt.year

    # Arrange columns
    df_dim_date = df_dim_date[
        [
            "Date ID",
            "Date",
            "Day",
            "Month",
            "Year"
        ]
    ]

    # ==========================================================
    # 4. CREATE DIM_REGION
    # ==========================================================

    print("Creating Dim_Region...")

    # Connect Orders with People using Region
    df_dim_region = (
        df_orders[
            ["Region"]
        ]
        .drop_duplicates()
        .merge(
            df_people[
                [
                    "Region",
                    "Regional Manager"
                ]
            ].drop_duplicates(),
            on="Region",
            how="left"
        )
    )

    df_dim_region = (
        df_dim_region
        .sort_values(by="Region")
        .reset_index(drop=True)
    )

    # Create Region ID
    df_dim_region.insert(
        0,
        "Region ID",
        range(1, len(df_dim_region) + 1)
    )

    # Arrange columns
    df_dim_region = df_dim_region[
        [
            "Region ID",
            "Regional Manager",
            "Region"
        ]
    ]

    # ==========================================================
    # 5. CREATE DIM_PRODUCT
    # ==========================================================

    print("Creating Dim_Product...")

    df_dim_product = (
        df_orders[
            [
                "Product ID",
                "Category",
                "Sub-Category",
                "Product Name"
            ]
        ]
        .drop_duplicates(subset=["Product ID"])
        .reset_index(drop=True)
    )

    # ==========================================================
    # 6. CREATE DIM_CUSTOMER
    # ==========================================================

    print("Creating Dim_Customer...")

    df_dim_customer = (
        df_orders[
            [
                "Customer ID",
                "Customer Name",
                "Segment",
                "Country/Region",
                "City",
                "State/Province",
                "Postal Code"
            ]
        ]
        .drop_duplicates(subset=["Customer ID"])
        .reset_index(drop=True)
    )

    # Rename Country/Region to Country
    df_dim_customer = df_dim_customer.rename(
        columns={
            "Country/Region": "Country"
        }
    )

    # ==========================================================
    # 7. CREATE DIM_SHIPPING
    # ==========================================================

    print("Creating Dim_Shipping...")

    df_dim_shipping = (
        df_orders[
            ["Ship Mode"]
        ]
        .drop_duplicates()
        .sort_values(by="Ship Mode")
        .reset_index(drop=True)
    )

    # Create Ship ID
    df_dim_shipping.insert(
        0,
        "Ship ID",
        range(1, len(df_dim_shipping) + 1)
    )

    # ==========================================================
    # 8. CREATE DIM_ORDER_HEADER
    # ==========================================================

    print("Creating Dim_Order_Header...")

    # One record for each Order ID
    df_dim_order_header = (
        df_orders[
            [
                "Order ID",
                "Order Date",
                "Ship Date",
                "Ship Mode",
                "Customer ID",
                "Region"
            ]
        ]
        .drop_duplicates(subset=["Order ID"])
        .reset_index(drop=True)
    )

    # ----------------------------------------------------------
    # Connect Order Date with Dim_Date
    # ----------------------------------------------------------

    df_dim_order_header = df_dim_order_header.merge(
        df_dim_date[
            [
                "Date ID",
                "Date"
            ]
        ],
        left_on="Order Date",
        right_on="Date",
        how="left"
    )

    # Remove temporary Date column
    df_dim_order_header = df_dim_order_header.drop(
        columns=["Date"]
    )

    # ----------------------------------------------------------
    # Connect Ship Mode with Dim_Shipping
    # ----------------------------------------------------------

    df_dim_order_header = df_dim_order_header.merge(
        df_dim_shipping[
            [
                "Ship ID",
                "Ship Mode"
            ]
        ],
        on="Ship Mode",
        how="left"
    )

    # ----------------------------------------------------------
    # Connect Region with Dim_Region
    # ----------------------------------------------------------

    df_dim_order_header = df_dim_order_header.merge(
        df_dim_region[
            [
                "Region ID",
                "Region"
            ]
        ],
        on="Region",
        how="left"
    )

    # Arrange columns
    df_dim_order_header = df_dim_order_header[
        [
            "Order ID",
            "Date ID",
            "Order Date",
            "Ship Date",
            "Ship ID",
            "Customer ID",
            "Region ID"
        ]
    ]

    # ==========================================================
    # 9. CREATE FACT_ORDER_DETAIL
    # ==========================================================

    print("Creating Fact_Order_Detail...")

    df_fact_order_detail = df_orders[
        [
            "Order ID",
            "Product ID",
            "Sales",
            "Quantity",
            "Discount",
            "Profit"
        ]
    ].copy()

    # ==========================================================
    # 10. CREATE FACT_RETURNS
    # ==========================================================

    print("Creating Fact_Returns...")

    # Connect Orders with Returns using Order ID
    df_fact_returns = (
        df_orders[
            ["Order ID"]
        ]
        .drop_duplicates()
        .merge(
            df_returns[
                [
                    "Order ID",
                    "Returned"
                ]
            ].drop_duplicates(subset=["Order ID"]),
            on="Order ID",
            how="left"
        )
    )

    # Orders without a return record are considered not returned
    df_fact_returns["Returned"] = (
        df_fact_returns["Returned"]
        .fillna("No")
    )

    # Returned = Yes -> Return_Count = 1
    # Returned = No  -> Return_Count = 0
    df_fact_returns["Return_Count"] = (
        df_fact_returns["Returned"]
        .astype(str)
        .str.strip()
        .str.lower()
        .eq("yes")
        .astype(int)
    )

    # Arrange columns
    df_fact_returns = df_fact_returns[
        [
            "Order ID",
            "Returned",
            "Return_Count"
        ]
    ]

    # ==========================================================
    # 11. TRANSFORMATION SUMMARY
    # ==========================================================

    print()
    print("Transformation completed.")
    print()
    print("Data Warehouse DataFrames:")

    print(
        f"  Dim_Date          : "
        f"{len(df_dim_date):,} rows"
    )

    print(
        f"  Dim_Region        : "
        f"{len(df_dim_region):,} rows"
    )

    print(
        f"  Dim_Product       : "
        f"{len(df_dim_product):,} rows"
    )

    print(
        f"  Dim_Customer      : "
        f"{len(df_dim_customer):,} rows"
    )

    print(
        f"  Dim_Shipping      : "
        f"{len(df_dim_shipping):,} rows"
    )

    print(
        f"  Dim_Order_Header  : "
        f"{len(df_dim_order_header):,} rows"
    )

    print(
        f"  Fact_Order_Detail : "
        f"{len(df_fact_order_detail):,} rows"
    )

    print(
        f"  Fact_Returns      : "
        f"{len(df_fact_returns):,} rows"
    )

    # ==========================================================
    # 12. RETURN 8 DATAFRAMES
    # ==========================================================

    return (
        df_dim_date,
        df_dim_region,
        df_dim_product,
        df_dim_customer,
        df_dim_shipping,
        df_dim_order_header,
        df_fact_order_detail,
        df_fact_returns
    )