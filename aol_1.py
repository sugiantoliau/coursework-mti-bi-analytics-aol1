# aol_1.py

from fn_01_import_dataset import fn_import_dataset
from fn_02_data_extract import fn_data_extract
from fn_03_data_transformation import fn_data_transformation
from fn_04_data_load import fn_data_load


# ==========================================================
# 1. IMPORT RAW DATASET INTO POSTGRESQL
# ==========================================================

# fn_import_dataset()


# ==========================================================
# 2. EXTRACT DATA FROM POSTGRESQL
# ==========================================================

df_orders, df_people, df_returns = fn_data_extract()


# ==========================================================
# 3. TRANSFORM DATA
# ==========================================================

(
    df_dim_date,
    df_dim_region,
    df_dim_product,
    df_dim_customer,
    df_dim_shipping,
    df_dim_order_header,
    df_fact_order_detail,
    df_fact_returns
) = fn_data_transformation(
    df_orders,
    df_people,
    df_returns
)


# ==========================================================
# 4. LOAD TRANSFORMED DATA INTO DATA WAREHOUSE
# ==========================================================

fn_data_load(
    df_dim_date,
    df_dim_region,
    df_dim_product,
    df_dim_customer,
    df_dim_shipping,
    df_dim_order_header,
    df_fact_order_detail,
    df_fact_returns
)

