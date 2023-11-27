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
    #connect db
    with PostgresDB() as db:
        # print("prompt v1 ",prompt)
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
        # print("prompt v2 ",prompt)


        prompt = llm.add_cap_ref(
            prompt, 
            f"\n\nRespond in this format {RESPONSE_FORMAT}. I need to be able to easily parse the sql query from your response. Also THINK as a user, if your are user, what you INFORMATION you want to GET? because we have like 300+ columns then you should be able to KNOW what you want. And alway get columns name. And current year is {YEAR}. And make sure this query is able to instantly run.", RESPONSE_FORMAT, 
            f"""
            explaination of the sql query
            {START_SQL_DELIMITER}
            sql query exclusively as a raw text
            {END_SQL_DELIMITER}
"""
        )
        print("prompt v3 ",prompt)

        # prompt_response = llm.prompt(prompt)
        prompt_response = llm.chat_with_openai(prompt)
        
        print("---------------- PROMPT RESPONSE ----------------")

        print(prompt_response)


        sql_query = prompt_response.split(START_SQL_DELIMITER)[1].split(END_SQL_DELIMITER)[0].strip()

        print("sql_query--:\n ",sql_query)

        result = db.run_sql(sql_query)

        print("--------------- RESULT ---------------")

    

        print(result)
        


if __name__ == '__main__':
    main()