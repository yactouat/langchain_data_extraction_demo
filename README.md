# Langchain data extraction demo

## What is this?

In this beginner-level repo, we'll talk a little about LLMs instrumentation using Langchain, we'll:

- extract formatted JSON data from a natural language sentence
- get the same kind of data over the web by scraping it from random websites
- create the SQL schema for the extracted data and insert it into a database
- ask questions to the database and get the answers in natural language

## Prerequisites

- [`ollama`](https://ollama.com/) installed on your machine.

We expect that:

- you are able to run Python code 
- you know what a LLM is
- you have a very basic understanding of SQL
- you have a very basic understanding of web development

## What is Langchain?

[Langchain](https://python.langchain.com/docs/get_started/introduction) is a framework for developping applications powered by language models. It has a wide array of features and the community around it is very active.

## What is `ollama`

[`ollama`](https://ollama.com/) is a tool that allows you to run various LLMs locally using a very simple CLI.

I've personally installed Mistral and CodeLlama on my machine because they can run on my laptop.

## natural language

- `ollama run mistral` 
- I've asked the following question : `if I was to invest $100 in the stocks market right now, what should I invest in?`
- it answered something along the lines of =>

```
I cannot provide you with specific investment advice as I am an artificial intelligence and do not have the ability to analyze your personal financial situation or invest on your behalf. However, I
can suggest some general approaches for investing $100 in the stock market. Here are a few options:

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
investment advice and is for educational purposes only.
```

This is going to be the basis of our automated data extraction pipeline: find investment opportunities over the web, parse the unstructured information as a formatted JSON object, insert it into a database, ask questions to this db using natural language and get the answers in natural language as well. We'll go with the flow and see where that leads us.

**My final goal would be the acquire the skills, technique, tools to create this pipeline for any kind of data, on any subject, by starting with a simple question.**

## natural language to JSON

Now let's ask `mistral` to extract the JSON data from the answer it gave us: 

```
you are a data clerck, your job is to extract a nicely formatted and syntactically correct JSON object from the input text below delimited by dashes:
------------------------------------------------
some general approaches for investing $100 in the stock market. Here are a few options:

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
investment advice and is for educational purposes only.
```

Every time, I get back a poorly formatted JSON object with more or less the same keys and values:

```json
{
"approaches": [
    {
        "title": "Index Funds",
        "description": "Investing in a low-cost index fund that tracks a major stock market index like the S&P 500. Provides diversification and broad market exposure.",
        "risks": ""
    },
    {
        "title": "Exchange-Traded Funds (ETFs)",
        "description": "Investing in ETFs for broad market exposure with a single trade. Come in various sectors, industries, and asset classes.",
        "risks": ""
    },
    {
        "title": "Blue Chip Stocks",
        "description": "Investing in well-established, financially sound blue chip companies. Examples include Apple, Microsoft, Amazon, Alphabet (Google)",
        "risks": ""
    },
    {
        "title": "Diversified Portfolio",
        "description": "Building a diversified portfolio by investing in multiple industries or sectors to spread risk and potentially increase returns.",
        "risks": ""
    },
"general_info": [
        {
            "title": "Risks",
            "description": "All investments involve risks. Understand potential risks before making investment decisions."
        },
        {
            "title": "Long-Term Investment",
            "description": "Consider investing for the long term (5 years or more). Historically, stocks have generally trended upwards over extended periods.",
            "risks": ""
        }
        ],
        "note": {
            "title": "Important Note",
            "description": "This information should not be considered investment advice and is for educational purposes only. Consult with a financial advisor before deciding on an investment strategy."
        }
    ]
}
```

... alright, let's try with `codellama` with the same prompt, I get back:

```json
{
    "some general approaches for investing $100 in the stock market": [
        {
            "option 1": "Index Funds",
            "description": "Consider investing in a low-cost index fund that tracks a major stock market index like the S&P 500. This option provides diversification and exposure to a wide range of companies, 
            which can help mitigate risk."
        },
        {
            "option 2": "Exchange-Traded Funds (ETFs)",
            "description": "Similar to index funds, ETFs are another investment vehicle that can provide broad market exposure with a single trade. They come in various sectors, industries, and asset classes, 
            allowing you to invest in specific areas of the market if desired."
        },
        {
            "option 3": "Blue Chip Stocks",
            "description": "Investing in well-established, financially sound blue chip companies could be an option for those who prefer individual stocks over funds. Companies like Apple, Microsoft, Amazon, 
            and Alphabet (Google) are examples of large, stable corporations that have a history of consistent earnings growth and dividend payments."
        },
        {
            "option 4": "Diversified Portfolio",
            "description": "You can also consider building a diversified portfolio by investing in multiple industries or sectors. This approach can help spread risk across various areas of the market and 
            potentially increase your chances of earning higher returns over time."
        }
    ],
    "potential risks": [
        "all investments involve risks", 
        "understand the potential risks before making an investment decision"
    ],
    "long-term investing": [
        "historical data shows that stocks have generally trended upwards over extended periods", 
        "invest for at least 5 years"
    ],
    "consideration of a financial advisor or thorough research": ["please note that this information should not be considered as personalized advice"]
}
```

It looks like `codellama` is doing a better job at outputting a nicely formatted JSON object, but on the other hand, `mistral` understands the information better and the way it organizes it, although it has trouble with the formatting. Let's try to mitigate this typical LLM issue [with a chain](./nl_to_json.py) !

## Our first LangChain chain

At first I tried to use `ollama` for both the extraction and the formatting part; as it happens, my laptop sucks so I had to use online inference endpoints, but the proof of concept is there and there are tools to speed up the process locally if I want to host this solution on premie (also, I may have better machines in a data center).

## Let's scale

Now that we have a way to extract data from an input text, let's [scale this up](./web_to_json.py) by gathering data from the web !

To do this we are going to:

- generate search engine web queries from the initial question `if I was to invest $100 in the stocks market right now, what should I invest in?`
- scrape the search engine results page (SERP) to get the URLs of the top results
- scrape the content of the top results to get the information we need
- extract the JSON data from the content of the top results

### Let's turn this into SQL

Now that we have a way to extract data from the web, let's [turn this data into SQL](./json_to_sql.py) !

We have a new superpower: create SQL data schemas on the fly from a natural language input question and a little pinch of web scraping 😎

We can now re inject our input data in our database and move on to asking questions to it.

## What I'm going to explore next

- look into `PowerInfer`, `LlamaCPP`, etc. to run models locally faster
- HuggingFace and/or Mistral inference endpoints
- understand [LCEL](https://python.langchain.com/docs/modules/model_io/prompts/quick_start#lcel) better
- LMMs (Gemini, GPT-4 vision, `bakllava`, etc.)
- Agent graphs