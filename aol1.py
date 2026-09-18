from fn_import_dataset import fn_import_dataset
from fn_data_extract import fn_data_extract
from fn_data_transformation import fn_data_transformation
from fn_data_load import fn_data_load


# 1. Import raw dataset into PostgreSQL
# fn_import_dataset()


# 2. Extract data from PostgreSQL
df_orders, df_people, df_returns = fn_data_extract()


# 3. Transform data
df_orders, df_people, df_returns = fn_data_transformation(
    df_orders,
    df_people,
    df_returns
)


# 4. Load transformed data into PostgreSQL
fn_data_load(
    df_orders,
    df_people,
    df_returns
)