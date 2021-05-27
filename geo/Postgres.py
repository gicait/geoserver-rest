from typing import Union

from psycopg2 import connect, sql


class Db:
    """
    Attributes
    ----------
    dbname : str, optional
        The name of the postgresql database.
    user : str
        Login name for session.
    password: str
        Password for session.
    host : str
        hostname of postgresql database
    port : int
    """

    def __init__(
        self,
        dbname=None,
        user="postgres",
        password="admin",
        host="localhost",
        port=5432,
    ):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port

        try:
            self.conn = connect(
                dbname=self.dbname,
                user=self.user,
                host=self.host,
                password=self.password,
            )

        except Exception as err:
            print("psycopg2 connect() ERROR:", err)
            self.conn = None

    # Execute sql query
    @staticmethod
    def execute_sql(cursor, sql_query: str):
        try:
            cursor.execute(sql_query)

        except Exception as err:
            print("ERROR: ", err)

    # get the columns names inside database
    def get_column_names(self, table: str):
        columns = list()
        with self.conn.cursor() as col_cursor:
            col_names_str = "SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = '{}';".format(
                table
            )
            sql_object = sql.SQL(col_names_str).format(sql.Identifier(table))
            try:
                col_cursor.execute(sql_object)
                col_names = col_cursor.fetchall()
                for tup in col_names:
                    columns += [tup[0]]

            except Exception as err:
                print("get_column_names ERROR:", err)

        return columns

    # get numberic columns names inside database

    def get_numeric_column_names(self, table: str):
        columns = list()
        with self.conn.cursor() as col_cursor:
            col_names_str = """
                            SELECT col.column_name FROM INFORMATION_SCHEMA.COLUMNS as col 
                            WHERE table_name = '{}' 
                                AND col.data_type in ('smallint', 'integer', 'bigint', 'decimal', 'numeric', 'real', 'double precision', 'smallserial', 'serial', 'bigserial', 'money');
                            """.format(table)

            sql_object = sql.SQL(col_names_str).format(sql.Identifier(table))
            try:
                col_cursor.execute(sql_object)
                col_names = col_cursor.fetchall()
                for tup in col_names:
                    columns += [tup[0]]

            except Exception as err:
                print("get_numeric_column_names ERROR:", err)

        return columns

    # get all the values from specific column

    def get_all_values(
        self, column: str, table: str, schema: str, distinct: bool = True
    ):
        values = []
        with self.conn.cursor() as col_cursor:
            if distinct:
                all_values_str = (
                    """SELECT DISTINCT "{0}" FROM "{2}"."{1}" ORDER BY "{0}";""".format(
                        column, table, schema
                    )
                )
            else:
                all_values_str = (
                    """SELECT "{0}" FROM "{2}"."{1}" ORDER BY "{0}";""".format(
                        column, table, schema
                    )
                )

            sql_object = sql.SQL(all_values_str).format(
                sql.Identifier(column), sql.Identifier(table)
            )

            try:
                col_cursor.execute(sql_object, column)
                values_name = col_cursor.fetchall()
                for tup in values_name:
                    values += [tup[0]]

            except Exception as err:
                print("get_all_values ERROR:", err)

        return values

    # create the schema based on the given name
    def create_schema(self, name: str):  # dbname="postgres"
        n = name.split(" ")
        if len(n) > 0:
            name = name.replace(" ", "_")

        with self.conn.cursor() as cursor:
            sql_query = f"""CREATE SCHEMA IF NOT EXISTS {name}"""
            self.execute_sql(cursor, sql_query)
            self.conn.commit()
            print("Schema create successfully")

    # create new column in table
    def create_column(
        self, col_name: str, table: str, schema: str, col_datatype: str = "varchar"
    ):

        with self.conn.cursor() as cursor:
            sql_query = (
                """ALTER TABLE "{3}"."{0}" ADD IF NOT EXISTS "{1}" {2}""".format(
                    table, col_name, col_datatype, schema
                )
            )
            self.execute_sql(cursor, sql_query)
            self.conn.commit()
            print("create column successful")

    # update column
    def update_column(
        self,
        column: str,
        value: Union[str, float, int],
        table: str,
        schema: str,
        where_col: str,
        where_val: str,
    ):
        with self.conn.cursor() as cursor:
            sql_query = """
                UPDATE "{}"."{}" SET "{}"='{}' WHERE "{}"='{}'
                """.format(
                schema, table, column, value, where_col, where_val
            )
            self.execute_sql(cursor, sql_query)
            self.conn.commit()
            print("update table successful")

    # delete table
    def delete_table(self, table_name: str, schema: str):
        with self.conn.cursor() as cursor:
            sql_query = """DROP TABLE IF EXISTS "{}"."{}" CASCADE;""".format(
                schema, table_name
            )
            self.execute_sql(cursor, sql_query)
            self.conn.commit()
            print("{} table dropped successfully.".format(table_name))

    # Delete values
    def delete_values(self, table_name: str, schema: str, condition: str):
        with self.conn.cursor() as cursor:
            sql_query = """DELETE FROM "{}"."{}" WHERE {}""".format(
                schema, table_name, condition
            )
            self.execute_sql(cursor, sql_query)
            self.conn.commit()
            print("Values dropped successfully.")
