from dotenv import load_dotenv
import os
from modules.db import PostgresDB
from modules import llmlocal as llm
import datetime
import argparse
load_dotenv()

os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
os.environ['DB_URL'] = os.getenv('DB_URL')

POSTGRES_TABLE_DEFINITIONS_CAP_REF = "TABLE_DEFINITIONS"
POSTGRES_SQL_QUERY_CAP_REF = "SQL_QUERY"
RESPONSE_FORMAT = "RESPONSE_FORMAT"



YEAR = datetime.datetime.now().year
START_SQL_DELIMITER = "--- SQL Query ---"
END_SQL_DELIMITER = "--- End SQL Query ---"

def main():
    #args parse
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", help="The prompt for the AI")
    parser.add_argument("--prompt-s",action='store_true',help = "Using specific table definitions")
    args = parser.parse_args()

    if not args.prompt:
        print("Please provide a prompt")
        return

    prompt = args.prompt
    with PostgresDB() as db:
        db.connect_with_url(os.environ['DB_URL'])

        if args.prompt_s:
            #add specific table names you want
            table_names = ['crm_lead','crm_lost_reason','crm_recurring_plan','crm_stage','mail_activity','res_partner']
            table_definitions = db.get_multiple_table_definitions_for_prompt(table_names)
        else:
        
            table_definitions = db.get_table_definitions_for_prompt()

        # print("table_definitions\n ",table_definitions)

        prompt = llm.add_cap_ref(
            args.prompt,
            f"\n\nUse these {POSTGRES_TABLE_DEFINITIONS_CAP_REF} to satisfy the database query.",
            POSTGRES_TABLE_DEFINITIONS_CAP_REF,
            table_definitions,
        )
        
        """
        pipline:
            Build the gpt_configuration object

            build the function map

            create our terminate msg function

            
            create a set of agents with specific roles
                admin user proxy agent - take the prompt and manages the group chat
                data engineer agent - generate sql query
                senior data analyst agent - run the sql query and generate the response
                product manager - validate the response to make sure it's correct

            create a group chat and initiate the chat
        """

        #function map
        function_map  ={
            "run_sql": db.run_sql,
        }
        


if __name__ == '__main__':
    main()