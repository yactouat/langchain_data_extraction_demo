from dotenv import load_dotenv
load_dotenv()

import json
from langchain_community.chat_models import ChatOllama, ChatOpenAI
from langchain_community.llms import Ollama
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough

from lib import (
    get_serp_links,
    scrape_webpage_text
)
from prompts import (
    extracting_prompt,
    formatting_prompt,
    web_search_engine_queries_prompt
)

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

res = json_web_extraction_chain.invoke({
    "query": "if I was to invest $100 in the stocks market right now, what should I invest in?"
})
print(res["output"])