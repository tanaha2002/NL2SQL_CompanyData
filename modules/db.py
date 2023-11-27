import psycopg2

class PostgresDB:
    def __init__(self):
        self.conn = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.conn:
            self.conn.close()


    def connect_with_url(self, url):
        self.conn = psycopg2.connect(url)

    def upsert(self, table_name, _dict):
        keys = _dict.keys()
        columns = ', '.join(keys)
        values = ', '.join(['%s' for _ in keys])
        update_str = ', '.join([f"{key} = EXCLUDED.{key}" for key in keys])
        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({values}) ON CONFLICT (id) DO UPDATE SET {update_str};"
        with self.conn.cursor() as cur:
            cur.execute(sql, tuple(_dict.values()))
            self.conn.commit()

    def delete(self, table_name, _id):
        sql = f"DELETE FROM {table_name} WHERE id = %s;"
        with self.conn.cursor() as cur:
            cur.execute(sql, (_id,))
            self.conn.commit()

    def get(self, table_name, _id):
        sql = f"SELECT * FROM {table_name} WHERE id = %s;"
        with self.conn.cursor() as cur:
            cur.execute(sql, (_id,))
            return cur.fetchone()

    def get_all(self, table_name):
        sql = f"SELECT * FROM {table_name};"
        with self.conn.cursor() as cur:
            cur.execute(sql)
            return cur.fetchall()

    def run_sql(self, sql):
        try:
            with self.conn.cursor() as cur:
                cur.execute(sql)
                self.conn.commit()
                return cur.fetchall()
        except Exception as e:
            print(f"ERROR: {e}")
            return None

    # def get_table_definitions(self, table_name):
    #     sql = f"SELECT pg_get_tabledef('{table_name}');"
    #     with self.conn.cursor() as cur:
    #         cur.execute(sql)
    #         return cur.fetchone()[0]

    def get_all_table_names(self):
        sql = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
        with self.conn.cursor() as cur:
            cur.execute(sql)
            return [row[0] for row in cur.fetchall()]
    def get_table_definitions(self, table_name):
        try:
            sql = f"SELECT table_schema, table_name, column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = %s;"
            with self.conn.cursor() as cur:
                cur.execute(sql, (table_name,))
                return cur.fetchall()
        except Exception as e:
            #commit
            self.conn.commit()
            print(f"Error: {e}")
            

    def get_specific_table_definition(self, table_name):
        columns = self.get_table_definitions(table_name)
        create_table_sql = f"CREATE TABLE {table_name} (\n"
        for column in columns:
            column_name = column[2]
            data_type = column[3]
            is_nullable = column[4]
            create_table_sql += f"    {column_name} {data_type}"
            if is_nullable == 'NO':
                create_table_sql += " NOT NULL"
            create_table_sql += ",\n"
        create_table_sql = create_table_sql.rstrip(",\n") + "\n);"
        return create_table_sql

    def get_top_n_rows(self, table_name, n=5):
        # Fetch column names
        query_columns = f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}';"
        columns_result = self.run_sql(query_columns)
        column_names = [row[0] for row in columns_result]

        # Fetch top N rows
        query_data = f"SELECT * FROM {table_name} LIMIT {n};"
        data_result = self.run_sql(query_data)

        # Format header with adjusted spaces
        max_lengths = [len(name) for name in column_names]
        formatted_output = ""
        for row in data_result:
            for i, cell in enumerate(row):
                cell_length = len(str(cell))
                if cell_length > max_lengths[i]:
                    max_lengths[i] = cell_length

        for i, name in enumerate(column_names):
            formatted_output += f"{name.ljust(max_lengths[i] + 2)}"

        formatted_output += "\n"

        # Format rows with adjusted spaces
        for row in data_result:
            for i, cell in enumerate(row):
                formatted_output += f"{str(cell).ljust(max_lengths[i] + 2)}"
            formatted_output += "\n"

        return formatted_output



        


    def get_multiple_table_definitions_for_prompt(self, table_names, n=3):
        table_definitions = []
        for table_name in table_names:
            table_def = self.get_specific_table_definition(table_name)
            top_n_rows = self.get_top_n_rows(table_name, n)
            
            table_def_with_sample = f"{table_def}\n\n-- Top {n} rows sample:\n"
            formatted_sample = top_n_rows  # Assuming top_n_rows already returns formatted output
            table_def_with_sample += formatted_sample
            
            table_definitions.append(table_def_with_sample)
        
        return '\n'.join(table_definitions)

        
    





    def close_cursor(self):
        self.conn.cursor().close()
    