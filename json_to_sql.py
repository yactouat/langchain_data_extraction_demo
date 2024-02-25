from dotenv import load_dotenv
load_dotenv()

import json
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.chat_models import ChatOllama, ChatOpenAI
from langchain_community.llms import Ollama
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from langchain_community.utilities import sql_database
import os
import sqlite3

from lib import (
    get_serp_links,
    scrape_webpage_text
)
from prompts import (
    extracting_prompt,
    formatting_prompt,
    json_to_sql_prompt,
    sql_write_agent_prompt,
    web_search_engine_queries_prompt
)

# delete example database if it exists
if os.path.exists('example.db'):
    os.remove('example.db')

gpt3dot5 = ChatOpenAI(model="gpt-3.5-turbo-0125")
gpt4 = ChatOpenAI(model="gpt-4-0125-preview")

# ! json chain
json_chain = RunnablePassthrough.assign(
    json=extracting_prompt | gpt4
).assign(
    formatted=formatting_prompt | gpt4 | StrOutputParser()
).assign(
    output=lambda x: json.loads(x["formatted"].replace("```json\n", "").replace("```", ""))
)

# ! web chains
web_queries_chain = web_search_engine_queries_prompt | gpt3dot5 | StrOutputParser() | json.loads
webpage_text_chain = RunnablePassthrough.assign(
    content=lambda input_obj: scrape_webpage_text(input_obj["url"])
)
web_search_chain = web_queries_chain | (lambda queries: [
    {
        "query": q,
    } for q in queries
]) | webpage_text_chain.map()
web_searches_chain = RunnablePassthrough.assign(
    urls=lambda input: get_serp_links(input["query"])
) | (lambda list_of_urls: [
    {
        "query": list_of_urls["query"],
        "url": link
    } for link in list_of_urls["urls"]
]) | webpage_text_chain.map()
web_search_extraction_chain = RunnablePassthrough.assign(
    input_text= web_searches_chain
) | (lambda x: "\n\n".join([input["content"] for input in x["input_text"]]))
json_web_extraction_chain = RunnablePassthrough.assign(
    input_text= web_search_extraction_chain
) | json_chain 

# ! SQL chains
json_to_sql_chain = RunnablePassthrough.assign(
    input_text= web_search_extraction_chain
) | json_chain | RunnablePassthrough.assign(
    json_schema=lambda x: x["output"]
) | json_to_sql_prompt | gpt4 | StrOutputParser()

res = json_to_sql_chain.invoke({
    "query": "if I was to invest $100 in the stocks market right now, what should I invest in?"
})
print(res)

conn = sqlite3.connect('example.db')
c = conn.cursor()
c.executescript(res.replace("```sql\n", "").replace("```", ""))
conn.commit()
conn.close()

# re inject our scraped data in our newly created database
db = sql_database.SQLDatabase.from_uri("sqlite:///example.db")
nl_to_db_writes_chain = create_sql_agent(gpt4, db=db, agent_type="openai-tools", verbose=True, prompt=sql_write_agent_prompt)
re_injection_chain = RunnablePassthrough.assign(
    input= json_to_sql_chain
) | nl_to_db_writes_chain
 
res = re_injection_chain.invoke({
    "query": "if I was to invest $100 in the stocks market right now, what should I invest in?"
})
print("database re-injection successful")
