import os
import sqlite3

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from tabulate import tabulate



def get_llm():
    api_key = os.getenv("DASHSCOPE_APIKEY")
    if not api_key:
        raise ValueError("请设置 DASHSCOPE_APIKEY 环境变量")
    return ChatOpenAI(
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        model="qwen-max",
    )




if __name__ == "__main__":
    
# 检查 API 密钥是否存在
    api_key = os.getenv("DASHSCOPE_APIKEY")
    if not api_key:
        raise ValueError("请设置 DASHSCOPE_APIKEY 环境变量")
    llm = get_llm()
    json_schema = {
        "title": "joke",
        "description": "Joke to tell user.",
        "type": "object",
        "properties": {
            "setup": {
                "type": "string",
                "description": "The setup of the joke",
            },
            "punchline": {
                "type": "string",
                "description": "The punchline to the joke",
            },
            "rating": {
                "type": "integer",
                "description": "How funny the joke is, from 1 to 10",
                "default": None,
            },
        },
        "required": ["setup", "punchline"],
    }
    structured_llm = llm.with_structured_output(json_schema)

    res = structured_llm.invoke("Tell me a joke about dogs and return it in JSON format")
    print(res)
