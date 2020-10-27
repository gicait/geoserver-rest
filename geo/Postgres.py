from psycopg2 import sql, connect
from psycopg2.extensions import quote_ident

db_name = 'geonode_data'


class Db:
    def __init__(self, dbname=None, user='postgres', password='admin', host='localhost', port=5432):
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
                password=self.password
            )

            print("psycopg2 connection:", self.conn)

        except Exception as err:
            print("psycopg2 connect() ERROR:", err)
            self.conn = None

    # get the columns names inside database

    def get_columns_names(self, table):
        try:
            columns = []
            col_cursor = self.conn.cursor()
            col_names_str = "SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE "
            col_names_str += "table_name = '{}';".format(table)
            sql_object = sql.SQL(col_names_str).format(sql.Identifier(table))

            col_cursor.execute(sql_object)
            col_names = (col_cursor.fetchall())

            for tup in col_names:
                columns += [tup[0]]
            col_cursor.close()

            return columns

        except Exception as err:
            print("get_columns_names ERROR:", err)

    def get_all_values(self, column, table, schema, distinct=True):
        try:
            values = []
            col_cursor = self.conn.cursor()
            if distinct:
                all_values_str = '''SELECT DISTINCT "{0}" FROM "{2}"."{1}" ORDER BY "{0}";'''.format(
                    column, table, schema)
            else:
                all_values_str = '''SELECT "{0}" FROM "{2}"."{1}" ORDER BY "{0}";'''.format(
                    column, table, schema)

            sql_object = sql.SQL(all_values_str).format(
                sql.Identifier(column), sql.Identifier(table))

            col_cursor.execute(sql_object, (column))
            values_name = (col_cursor.fetchall())

            for tup in values_name:
                values += [tup[0]]
            col_cursor.close()

            return values

        except Exception as err:
            print("get_columns_names ERROR:", err)

    # create the schema based on the given name

    def create_schema(self, name, dbname='postgres'):
        try:
            n = name.split(' ')
            if len(n) > 0:
                name = name.replace(' ', '_')
            cursor = self.conn.cursor()

            sql = f'''CREATE SCHEMA IF NOT EXISTS {name}'''
            cursor.execute(sql)
            self.conn.commit()
            cursor.close()

            print('Schema create successfully')

        except Exception as err:
            print('Schema create error: ', err)

    # create new column in table

    def create_column(self, col_name, table, schema, col_datatype='varchar'):
        try:
            cursor = self.conn.cursor()
            sql = '''ALTER TABLE "{3}"."{0}" ADD {1} {2}'''.format(
                table, col_name, col_datatype, schema)
            cursor.execute(sql)
            self.conn.commit()
            cursor.close()
            print('create column successful')

        except Exception as err:
            print('Create column error: ', err)

    # update column

    def update_column(self, column, value, table, schema, where_col, where_val):
        try:
            cursor = self.conn.cursor()
            sql = '''
            UPDATE "{0}"."{1}" SET "{2}"='{3}' WHERE "{4}"='{5}'
            '''.format(
                schema, table, column, value, where_col, where_val)
            cursor.execute(sql)
            self.conn.commit()
            cursor.close()
            print('update table successful')

        except Exception as err:
            print('update table error: ', err)

    # delete table

    def delete_table(self, table_name, schema, dbname='postgres'):
        try:
            cursor = self.conn.cursor()
            sql = '''DROP TABLE IF EXISTS "{}"."{}" CASCADE;'''.format(
                schema, table_name)

            cursor.execute(sql)
            self.conn.commit()
            cursor.close()
            print('{} table dropped successfully.'.format(table_name))

        except Exception as err:
            print('Delete table error: ', err)
