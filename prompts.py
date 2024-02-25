from langchain_core.prompts import MessagesPlaceholder
from langchain.prompts import ChatPromptTemplate

# ! JSON prompts
extracting_prompt_template = """Given the following input text, delimited by dashes extract a nicely formatted and syntactically correct JSON object without any preamble or explanation:
-----------------------------------------------------------------------------------------------------------
{input_text}"""
extracting_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "you are a data clerck, your job is to extract a nicely formatted and syntactically correct JSON objects from text, without any preamble or explanation"),
        ("user", extracting_prompt_template),
    ]
)

formatting_prompt_template = """With the following input JSON object, delimited by dashes, format it so that it is syntatically correct:
-----------------------------------------------------------------------------------------------------------
{json}
-----------------------------------------------------------------------------------------------------------
If the input JSON object is already syntactically correct, just output the input JSON object.
Do not add any pre amble or explanation to the output.
If the input JSON object is an array of objects, make sure that all the objects have the same keys."""
formatting_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "you are a data clerk, your job is to format JSON objects so that the are syntactically correct"),
        ("user", formatting_prompt_template),
    ]
)

# ! web search prompts
web_search_engine_queries_prompt_template = [
    ("user", """write 3 web search engine queries to search online for an objective answer to the following query: {query}\n
-----------------------------------------------------------------------------------------------------------
you must respond with a list of strings in the following format: '["query 1", "query 2", "query 3"]'""")
]
web_search_engine_queries_prompt = ChatPromptTemplate.from_messages(web_search_engine_queries_prompt_template)

# ! SQL prompts
json_to_sql_prompt_template = """Based on the JSON schema(s) below, delimited with dashes, write the SQLite code that would create the table(s) that would best fit this schema:
-----------------------------------------------------------------------------------------------------------
{json_schema}
-----------------------------------------------------------------------------------------------------------
Your output will only contain the raw SQL code, without any formatting, explanations, or pre-amble.
Do not hesitate to create multiple tables to reflect the structure of the JSON schema."""
json_to_sql_prompt = ChatPromptTemplate.from_messages([
    ("system", "Given a JSON schema, convert it into a SQL schema. No pre-amble."),
    ("user", json_to_sql_prompt_template)
])

sql_write_agent_prompt_template = """You are an agent designed to interact with a SQL database.
Given an input unstructured text, create a syntactically correct {dialect} query to run in order to insert the corresponding entries in the existing database schema.
You have access to tools for interacting with the database.
Only use the given tools. Only use the information returned by the tools to construct your final answer.

You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.

You can insert and update entries in the database.

If the input unstructured text is not exactly related to the database schema, try to insert/update as much information as you can in the most relevant table in the database."""
sql_write_agent_prompt = ChatPromptTemplate.from_messages([
    ("system", sql_write_agent_prompt_template),
    ("user", "{input}"),
    # prompt that assumes that the input is a list of messages
    MessagesPlaceholder("agent_scratchpad"),
])
