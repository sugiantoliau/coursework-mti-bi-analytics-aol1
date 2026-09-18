from fn_db_function import fn_db_connection

with fn_db_connection() as vl_dbconn:
    with vl_dbconn.cursor() as cur:
        cur.execute("SELECT version();")
        print(cur.fetchone()[0])

        vl_sql_stat = "create table testtable (key int, f_name varchar(50), f_age int);"
        cur.execute(vl_sql_stat)
        vl_dbconn.commit()
        print('create table testtable')

        vl_sql_stat = "insert into testtable (key, f_name, f_age)"
        vl_sql_stat += " values (%s, %s, %s);"
        vl_sql_data = ('01', 'budi', '3') 
        cur.execute(vl_sql_stat, vl_sql_data)        
        vl_dbconn.commit()

        cur.execute("SELECT * from testtable;")
        print(cur.fetchall())

        vl_sql_stat = "update testtable set f_name='andi' where f_name='budi';"        
        cur.execute(vl_sql_stat)        
        vl_dbconn.commit()

        cur.execute("SELECT * from testtable;")
        print(cur.fetchall())

        vl_sql_stat = "delete from testtable;"        
        cur.execute(vl_sql_stat)        
        vl_dbconn.commit()
        print('clear table testtable')

        vl_sql_stat = "drop table testtable;"
        cur.execute(vl_sql_stat)
        vl_dbconn.commit()
        print('drop table testtable')

        
        