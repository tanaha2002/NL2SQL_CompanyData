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

        with self.conn.cursor() as cur:
            cur.execute(sql)
            self.conn.commit()
            
            return cur.fetchall(),cur.description
        

    def get_table_definitions(self, table_name):
        sql = f"SELECT pg_get_tabledef('{table_name}');"
        with self.conn.cursor() as cur:
            cur.execute(sql)
            return cur.fetchone()[0]

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
            
    
            
    def get_column_names(self):
        table_details = {
    'res_company': {
        'id': 'id of the company',
        'name': 'Name of the company'
    },
    'crm_lead': {
        '_id': 'id of the opportunity, project',
        'campaign_id': 'id from utm_campaign table',
        'source_id': 'id from utm_source table',
        'medium_id': 'id from utm_medium table',
        'userid': 'id from res_users table',
        'team_id': 'id from crm_team table',
        'company_id': 'id from res_company table',
        'stage_id': 'id from crm_stage table',
        'lost_reason_id': 'id from crm_lost_reason table',
        'phone_sanitized': 'Phone number of the customer',
        'email_normalized': 'Email of the customer',
        'name': 'Name of the opportunity',
        'contact_name': 'Linked partner through the contact module',
        'partner_name': 'Name of the contacting company',
        'function': 'Position of the contact person',
        'email_from': 'Email of the customer',
        'phone': 'Phone number of the customer',
        'website': 'Website of the contacting company',
        'street': 'Address of the contacting company',
        'street2': 'Additional address information',
        'zip': 'Zip code of the contacting company',
        'city': 'City of the contacting company',
        'date_deadline': 'Expected project end date of the opportunity',
        'description': 'Internal notes of the opportunity',
        'expected_revenue': 'Expected revenue of the opportunity',
        'date_open': 'Date when the opportunity was created',
        'probability': 'Success probability of the opportunity',
        'referred': 'Contact person of the company'
    },
    'res_users': {
        'id': 'id of the user',
        'partner_id': 'id from res_partner table'
    },
    'crm_stage': {
        'id': 'id of the stage',
        'name': 'Stage name (json format. Example: {"en_US": "New"})',
    },
    'crm_tag_rel': {
        'lead_id': 'id of the crm_lead table',
        'tag_id': 'id from crm_tag table'
    },
    'crm_tag': {
        'id': 'id of the tag',
        'name': 'Name for classification'
    },
    'crm_lost_reason': {
        'id': 'id of the lost reason',
        'name': 'Reason for opportunity loss'
    },
    'utm_campaign': {
        'id': 'id of the campaign',
        'name': 'Name of the campaign'
    },
    'utm_medium': {
        'id': 'id of the medium',
        'name': 'Name of the medium'
    },
    'utm_source': {
        'id': 'id of the source',
        'name': 'Name of the source'
    },
    'mail_activity': {
        'id': 'id of the activity',
        'res_name': 'Name of the activity',
        'summary': 'Summary of the activity',
        'date_deadline': 'Deadline of the activity'
    },
    'res_partner': {
        'id':'id of partner',
        'name': 'Name of the partner',
    }
    }
        return table_details
    
    def get_schema_linking_prompt(self, table_name):
        columns = self.get_table_definitions(table_name)
        table_details = self.get_column_names()
        create_table_sql = f"Table {table_name}, colums = [*"
        if table_name in table_details.keys():
            for column in columns:
                column_name = column[2]
                data_type = column[3]
                if column_name in table_details[table_name].keys():
                    create_table_sql += f",\n {column_name}: {data_type} -> column description: {table_details[table_name][column_name]}"
        create_table_sql +=  "]"
        return create_table_sql
            

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
        columns_result,description = self.run_sql(query_columns)
        #filter column with only column in table_details
        table_details = self.get_column_names()
        column_names = [row[0] for row in columns_result if row[0] in table_details[table_name].keys()]
        # column_names = [row[0] for row in columns_result]

        # Fetch top N rows with only column in table_details
        
        # query_data = f"SELECT * FROM {table_name} LIMIT {n};"
        query_data = f"SELECT {','.join(column_names)} FROM {table_name} LIMIT {n};"
        data_result,description = self.run_sql(query_data)

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
            table_def = self.get_schema_linking_prompt(table_name)
            top_n_rows = self.get_top_n_rows(table_name, n)
            
            table_def_with_sample = f"{table_def}\n-- {n} rows sample:\n\n"
            formatted_sample = top_n_rows  # Assuming top_n_rows already returns formatted output
            table_def_with_sample += formatted_sample
            
            table_definitions.append(table_def_with_sample)
        
        
        return '\n'.join(table_definitions)

        


    def close_cursor(self):
        self.conn.cursor().close()
    
    
