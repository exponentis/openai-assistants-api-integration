import openai_access


def create_assistant():
    asst = openai_access.create_assistant(
        "TestAssistant",
        "gpt-4-1106-preview",
        """You are an expert in the stock market and able to provide up to date info on stock prices 
        and advice on buy/sell decisions""",
        tools_list,
        []
    )
    print(asst)
    return asst


tools_list = [
    {
        "type": "function",
        "function": {
            "name": "get_stock_price",
            "description": "Retrieve the latest closing price of a stock using its ticker symbol",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "The ticker symbol of the stock"
                    }
                },
                "required": ["symbol"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "buy_or_sell",
            "description": "Make a decision on buying or selling a stock, given it's symbol and price",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "The ticker symbol of the stock"
                    },
                    "price": {
                        "type": "string",
                        "description": "The price of the stock"
                    }
                },
                "required": ["symbol", "price"]
            }
        }
    }
]

if __name__ == '__main__':
    create_assistant()

