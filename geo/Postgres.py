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
                dbname = self.dbname,
                user = self.user,
                host = self.host,
                password = self.password
            )

            print ("psycopg2 connection:", self.conn)

        except Exception as err:
            print ("psycopg2 connect() ERROR:", err)
            self.conn = None


    # get the columns names inside database
    def get_columns_names(self, table):
        columns = []
        col_cursor = self.conn.cursor()
        col_names_str = "SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE "
        col_names_str += "table_name = '{}';".format( table )

        try:
            sql_object = sql.SQL(col_names_str).format(sql.Identifier( table ))

            col_cursor.execute( sql_object )
            col_names = ( col_cursor.fetchall() )

            for tup in col_names:
                columns += [ tup[0] ]
            col_cursor.close()

        except Exception as err:
            print ("get_columns_names ERROR:", err)

        return columns


    # get the distinct values of specific column
    def get_all_values(self, table, column, distinct=True):
        values = []
        col_cursor = self.conn.cursor()
        if distinct:
            all_values_str = '''SELECT DISTINCT "{0}" FROM "{1}";'''.format(column, table)

        all_values_str = '''SELECT "{0}" FROM "{1}";'''.format(column, table)

        try:
            sql_object = sql.SQL(all_values_str).format(sql.Identifier(column), sql.Identifier(table))

            col_cursor.execute( sql_object, (column) )
            values_name = ( col_cursor.fetchall() )

            for tup in values_name:
                values += [ tup[0] ]
            col_cursor.close()

        except Exception as err:
            print ("get_columns_names ERROR:", err)

        return values


    #create the schema based on the given name
    def create_schema(self, name, dbname='postgres'):
        try: 
            n = name.split(' ')
            if len(n)>0:
                name = name.replace(' ', '_')
            cursor = self.conn.cursor()

            sql = f'''CREATE SCHEMA {name}'''
            cursor.execute(sql)
            self.conn.commit()

            print('Schema create successfully')
        
        except Exception as err:
            print('Schema create error: ', err)
