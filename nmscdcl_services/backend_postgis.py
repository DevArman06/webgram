import psycopg2
from psycopg2 import sql as sqlbuilder
from psycopg2.extensions import quote_ident
import re
import random, string


class Introspect:
    def __init__(self, database, host='localhost', port='5432', user='postgres', password='postgres'):
        self.conn = None
        self.database = database
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.__enter__()

    def __enter__(self):
        if not self.conn:
            self.conn = psycopg2.connect(database=self.database, user=self.user, password=self.password, host=self.host, port=self.port)
            delattr(self, 'user')
            delattr(self, 'password')
            self.conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
            self.cursor = self.conn.cursor()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()
        return exc_type is None

    def get_geoserver_view_pk_columns(self, schema, table):
        try:
            query = sqlbuilder.SQL("""
            SELECT pk_column FROM {schema}.gt_pk_metadata WHERE table_name = %s AND table_schema = %s
            """).format(schema=sqlbuilder.Identifier(schema))
            self.cursor.execute(query, [table, schema])
            return [r[0] for r in self.cursor.fetchall()]
        except:
            # the table may not exist, this is not an error
            return []

    def get_pk_columns(self, table, schema='public'):
        qualified_table = quote_ident(schema, self.conn) + "." + quote_ident(table, self.conn) 

        query = sqlbuilder.SQL("""
        SELECT a.attname AS field_name
                        FROM pg_index i
                        JOIN pg_attribute a ON a.attrelid = i.indrelid
                        AND a.attnum = ANY(i.indkey)
                        WHERE
                        i.indrelid = ({schema_table})::regclass
                        AND i.indisprimary
        """).format(schema_table=sqlbuilder.Literal(qualified_table))
        self.cursor.execute(query)
        pks = self.cursor.fetchall()
        if len(pks) == 0 and self.is_view(schema, table):
            return self.get_geoserver_view_pk_columns(schema, table)
        return [r[0] for r in pks]

    def get_fields(self, table, schema='public'):
        self.cursor.execute("""
        SELECT column_name FROM information_schema.columns
        WHERE table_schema = %s AND table_name = %s 
        """, [schema, table])
        
        return [r[0] for r in self.cursor.fetchall()]

    def set_field_default(self, schema, table, field, default_value=None):
        """
        Sets a column default value. Use None to drop the default value of a column.
        Warning: 'default_value' parameter is not protected against SQL injection.
        Always validate user input to feed this parameter.
        """
        if default_value is None:
            sql = "ALTER TABLE {schema}.{table} ALTER COLUMN {field} DROP DEFAULT"
        else:
            sql = "ALTER TABLE {schema}.{table} ALTER COLUMN {field} SET DEFAULT " + default_value
        query = sqlbuilder.SQL(sql).format(
            schema=sqlbuilder.Identifier(schema),
            table=sqlbuilder.Identifier(table),
            field=sqlbuilder.Identifier(field))
        self.cursor.execute(query)

    def validate_data_type(self, data_type_def):
        """
        Returns a PostgreSQL data type if the provided data_type_def is valid,
        or None otherwise.
        """
        if data_type_def == 'character_varying' or data_type_def == 'character varying':
            return 'character varying'
        elif data_type_def == 'integer':
            return 'integer'
        elif data_type_def == 'double' or data_type_def == 'double precision':
            return 'double precision'
        elif data_type_def == 'boolean':
            return 'boolean'
        elif data_type_def == 'date':
            return 'date'
        elif data_type_def == 'time':
            return 'time'
        elif data_type_def == 'timestamp':
            return 'timestamp'
        elif data_type_def == 'timestamp_with_time_zone' or data_type_def == 'timestamp with time zone':
            return 'timestamp with time zone'
        elif data_type_def == 'cd_json':
            return 'character varying'
        elif data_type_def == 'enumeration' or \
                data_type_def == 'multiple_enumeration' or \
                data_type_def == 'form':
            return 'character varying'

    def add_column(self, schema, table_name, column_name, sql_type, nullable=True, default=None):
        """
        Warning: 'default' parameter is not protected against SQL injection. Always validate
        user input to feed this parameter.
        """
        data_type = self.validate_data_type(sql_type)
        if not data_type:
            raise Exception('Invalid data type')
        if not nullable:
            nullable_query = sqlbuilder.SQL("NOT NULL")
        else:
            nullable_query = sqlbuilder.SQL("")
        if default:
            default_query = sqlbuilder.SQL("DEFAULT " + default)
        else:
            default_query = sqlbuilder.SQL("")
        query = sqlbuilder.SQL("ALTER TABLE {schema}.{table} ADD COLUMN {column_name} {sql_type} {nullable} {default}").format(
            schema=sqlbuilder.Identifier(schema),
            table=sqlbuilder.Identifier(table_name),
            column_name=sqlbuilder.Identifier(column_name),
            sql_type=sqlbuilder.SQL(data_type),
            nullable=nullable_query,
            default=default_query)
        self.cursor.execute(query,  [])

    def get_pk_sequences(self, table, schema='public'):
        seqs = self.get_sequences(table, schema)
        pks = self.get_pk_columns(table, schema)
        result = []
        for (col, schema, seq_name) in seqs:
            if col in pks:
              result.append((col, schema, seq_name))
        return result

    def update_pk_sequences(self, table, schema='public'):
        """
        Ensures the sequence start value is higher than any existing value for the column.
        We combine max(id) and last_value because we want to modify the sequence ONLY if
        'last_value' is smaller than the maximum id value.
        """
        seqs = self.get_pk_sequences(table, schema)
        sql = """SELECT setval({seq}, s3.next_val) FROM
                    (SELECT GREATEST(max_id, last_value) next_val from
                    (SELECT last_value from {seq_schema}.{seq_name}) s1,
                    (SELECT MAX({col}) max_id from {schema}.{table}) s2) s3"""
        for (col, seq_schema, seq_name) in seqs:
            full_sequence = quote_ident(seq_schema, self.conn) + "." + quote_ident(seq_name, self.conn)
            query = sqlbuilder.SQL(sql).format(
                seq=sqlbuilder.Literal(full_sequence),
                seq_schema=sqlbuilder.Identifier(seq_schema),
                seq_name=sqlbuilder.Identifier(seq_name),
                col=sqlbuilder.Identifier(col),
                schema=sqlbuilder.Identifier(schema),
                table=sqlbuilder.Identifier(table))
            self.cursor.execute(query)

    def delete_table(self, schema, table_name):
        query = sqlbuilder.SQL("DROP TABLE IF EXISTS {schema}.{table}").format(
            schema=sqlbuilder.Identifier(schema),
            table=sqlbuilder.Identifier(table_name))
        self.cursor.execute(query,  [])