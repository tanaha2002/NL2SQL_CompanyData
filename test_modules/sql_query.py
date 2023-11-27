from modules.db import PostgresDB
from modules import llm
import os
from dotenv import load_dotenv
load_dotenv()

with PostgresDB() as db:
    db.connect_with_url(os.environ['DB_URL'])
    prompt = f"""
Doanh thu của cơ hội nào lớn nhất? 

Use these TABLE_DEFINITIONS to satisfy the database query.

TABLE_DEFINITIONS

CREATE TABLE crm_lead (
    lang_id integer,
    campaign_id integer,
    source_id integer,
    medium_id integer,
    message_main_attachment_id integer,
    message_bounce integer,
    user_id integer,
    team_id integer,
    company_id integer,
    stage_id integer,
    color integer,
    recurring_plan integer,
    partner_id integer,
    title integer,
    id integer NOT NULL,
    state_id integer,
    country_id integer,
    lost_reason_id integer,
    create_uid integer,
    write_uid integer,
    date_deadline date,
    lead_properties jsonb,
    expected_revenue numeric,
    prorated_revenue numeric,
    recurring_revenue numeric,
    recurring_revenue_monthly numeric,
    recurring_revenue_monthly_prorated numeric,
    active boolean,
    date_closed timestamp without time zone,
    date_action_last timestamp without time zone,
    date_open timestamp without time zone,
    date_last_stage_update timestamp without time zone,
    date_conversion timestamp without time zone,
    create_date timestamp without time zone,
    write_date timestamp without time zone,
    day_open double precision,
    day_close double precision,
    probability double precision,
    automated_probability double precision,
    iap_enrich_done boolean,
    lead_mining_request_id integer,
    reveal_id character varying,
    phone_sanitized character varying,
    email_normalized character varying,
    email_cc character varying,
    name character varying NOT NULL,
    referred character varying,
    type character varying NOT NULL,
    priority character varying,
    contact_name character varying,
    partner_name character varying,
    function character varying,
    email_from character varying,
    phone character varying,
    mobile character varying,
    phone_state character varying,
    email_state character varying,
    website character varying,
    street character varying,
    street2 character varying,
    zip character varying,
    city character varying,
    description text
);
CREATE TABLE crm_lost_reason (
    id integer NOT NULL,
    create_uid integer,
    write_uid integer,
    name jsonb NOT NULL,
    active boolean,
    create_date timestamp without time zone,
    write_date timestamp without time zone
);
CREATE TABLE crm_recurring_plan (
    id integer NOT NULL,
    number_of_months integer NOT NULL,
    sequence integer,
    create_uid integer,
    write_uid integer,
    name jsonb NOT NULL,
    active boolean,
    create_date timestamp without time zone,
    write_date timestamp without time zone
);
CREATE TABLE crm_stage (
    write_date timestamp without time zone,
    sequence integer,
    team_id integer,
    create_uid integer,
    write_uid integer,
    name jsonb NOT NULL,
    id integer NOT NULL,
    is_won boolean,
    fold boolean,
    create_date timestamp without time zone,
    requirements text
);
CREATE TABLE mail_activity (
    calendar_event_id integer,
    res_model_id integer NOT NULL,
    res_id integer,
    activity_type_id integer,
    user_id integer NOT NULL,
    request_partner_id integer,
    recommended_activity_type_id integer,
    previous_activity_type_id integer,
    create_uid integer,
    write_uid integer,
    automated boolean,
    create_date timestamp without time zone,
    write_date timestamp without time zone,
    id integer NOT NULL,
    date_deadline date NOT NULL,
    res_model character varying,
    res_name character varying,
    summary character varying,
    note text
);
CREATE TABLE res_partner (
    company_id integer,
    title integer,
    parent_id integer,
    user_id integer,
    state_id integer,
    date date,
    country_id integer,
    partner_latitude numeric,
    partner_longitude numeric,
    active boolean,
    employee boolean,
    is_company boolean,
    partner_share boolean,
    write_date timestamp without time zone,
    message_main_attachment_id integer,
    message_bounce integer,
    industry_id integer,
    color integer,
    commercial_partner_id integer,
    signup_expiration timestamp without time zone,
    calendar_last_notif_ack timestamp without time zone,
    team_id integer,
    partner_gid integer,
    create_uid integer,
    id integer NOT NULL,
    write_uid integer,
    create_date timestamp without time zone,
    phone_sanitized character varying,
    name character varying,
    display_name character varying,
    ref character varying,
    lang character varying,
    tz character varying,
    vat character varying,
    company_registry character varying,
    website character varying,
    function character varying,
    type character varying,
    street character varying,
    street2 character varying,
    zip character varying,
    city character varying,
    email character varying,
    phone character varying,
    mobile character varying,
    commercial_company_name character varying,
    company_name character varying,
    comment text,
    email_normalized character varying,
    signup_token character varying,
    signup_type character varying,
    additional_info character varying
);

Respond in this format RESPONSE_FORMAT. I need to be able to easily parse the sql query from your response. Also THINK as a user, if your are user, what you INFORMATION you want to GET? because we have like 300+ columns then you should be able to KNOW what you want. And alway get columns name.      

RESPONSE_FORMAT


            <explaination of the sql query>
            --- SQL Query ---
            sql query exclusively as a raw text
            --- End SQL Query ---

"""
    # print(prompt)
    print("--------------------------------------------------")
    # query = llm.prompt(prompt)
    # result = db.run_sql(query)
    # print(result)
    # print(query)
    query = """SELECT id, name
FROM crm_lead
WHERE stage_id IN (
    SELECT id
    FROM crm_stage
    WHERE is_won = true
);"""
    result = db.run_sql(query)
    print(result)