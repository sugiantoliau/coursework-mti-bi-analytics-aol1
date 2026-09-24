# fn_db_function.py

from sqlalchemy import create_engine
from dotenv import dotenv_values

vl_config = dotenv_values(".env")


def fn_db_engine():

    connection_url = (
        f"postgresql+psycopg://"
        f"{vl_config['user']}:{vl_config['password']}"
        f"@{vl_config['host']}:{vl_config['port']}"
        f"/{vl_config['dbname']}"
        f"?sslmode={vl_config['sslmode']}"
    )

    return create_engine(connection_url)