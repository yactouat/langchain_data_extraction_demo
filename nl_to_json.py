from dotenv import load_dotenv
load_dotenv()

import json
from langchain_community.chat_models import ChatOllama, ChatOpenAI
from langchain_community.llms import Ollama
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough

# extractor_chat = ChatOllama(model="mistral")
# formatter_chat = ChatOllama(model="codellama")
gpt3dot5 = ChatOpenAI(model="gpt-3.5-turbo-0125")

input_text = """some general approaches for investing $100 in the stock market. Here are a few options:

1. Index Funds: Consider investing in a low-cost index fund that tracks a major stock market index like the S&P 500. This option provides diversification and exposure to a wide range of companies, 
which can help mitigate risk.

2. Exchange-Traded Funds (ETFs): Similar to index funds, ETFs are another investment vehicle that can provide broad market exposure with a single trade. They come in various sectors, industries, and
asset classes, allowing you to invest in specific areas of the market if desired.

3. Blue Chip Stocks: Investing in well-established, financially sound blue chip companies could be an option for those who prefer individual stocks over funds. Companies like Apple, Microsoft, 
Amazon, and Alphabet (Google) are examples of large, stable corporations that have a history of consistent earnings growth and dividend payments.

4. Diversified Portfolio: You can also consider building a diversified portfolio by investing in multiple industries or sectors. This approach can help spread risk across various areas of the market
and potentially increase your chances of earning higher returns over time.

It's essential to keep in mind that all investments involve risks, and it's important to understand the potential risks before making an investment decision. It's also a good idea to consider 
investing for the long term (5 years or more) as historical data shows that stocks have generally trended upwards over extended periods.

Additionally, you might want to consult with a financial advisor or do thorough research before deciding on an investment strategy. Please note that this information should not be considered 
investment advice and is for educational purposes only."""

extracting_prompt_template = """Given the following input text, delimited by dashes extract a nicely formatted and syntactically correct JSON object without any preamble or explanation:
-----------------------------------------------------------------------------------------------------------
{input_text}"""
extracting_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "you are a data clerck, your job is to extract a nicely formatted and syntactically correct JSON objects from text, without any preamble or explanation"),
        ("user", extracting_prompt_template),
    ]
)

formatting_prompt_template = """With the following JSON object, delimited by dashes, format it so that it is syntatically correct:
-----------------------------------------------------------------------------------------------------------
{json}
-----------------------------------------------------------------------------------------------------------
If the input JSON object is already syntactically correct, just output the input JSON object.
Do not add any pre amble or explanation to the output."""
formatting_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "you are a data clerk, your job is to format JSON objects so that the are syntactically correct"),
        ("user", formatting_prompt_template),
    ]
)

json_chain = RunnablePassthrough.assign(
    json=extracting_prompt | gpt3dot5
).assign(
    formatted=formatting_prompt | gpt3dot5 | StrOutputParser()
).assign(
    output=lambda x: json.loads(x["formatted"])
)

res = json_chain.invoke({
    "input_text": input_text
})
print(res["output"])