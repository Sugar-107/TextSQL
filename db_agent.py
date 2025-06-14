import os

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

from langchain.agents import initialize_agent
from langchain.agents import AgentType
from langchain_core.prompts import ChatPromptTemplate

from xiyan import mschema

from db_chat import run_sql_query

llm = ChatOpenAI(
    api_key=os.getenv("DASHSCOPE_APIKEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    model="qwen-max",
)


@tool
def file_saver(content: str, filename: str) -> str:
    """
    当需要写入文件的时候，可以使用该工具
    Args:
        content: 需要写入的文件内容
        filename: 文件名称
    """
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    return "文件写入成功"


@tool
def execute_sql(sql: str):
    """根据提供的sql语句来执行sql,并返回执行后的结果"""
    print(sql)
    return run_sql_query(sql)


agent = initialize_agent(
    tools=[execute_sql, file_saver],
    llm=llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
)

system_prompt = """
 你是一个能够进行数据分析的智能体，当用户输入数据分析需求时，你需要先将需求转换为可执行的sqlite支持的SQL，然后通过工具来执行SQL获取返回结果，
 最后总结SQL查询到的结果，当所有任务完成后，你需要通过工具生成一份数据分析报告并写到一份文件中。
                                     
 你可以一步一步来分析需求，最终确定需要生成的查询SQL。
 
 为了提高SQL生成的准确性，生成SQL后请对SQL的准确性进行评估，如果有问题则重新生成SQL
 
 当执行SQL失败时，你需要根据错误信息来修正SQL再重新尝试执行。
 
 ### 工具 ###
 execute_sql : 可以通过传入的SQL语句来执行SQL，并返回执行结果。
 file_saver: 当需要写入文件的时候，可以使用该工具。
 
"""

user_prompt = """
以下是我需要查询的数据库信息：
{schema}

我的需求是：{input}
"""

def invoke(msg: str):
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", user_prompt)

    ]).invoke({"input": msg, "schema": mschema()})

    return agent.invoke(prompt)


if __name__ == "__main__":
    invoke("Could you help me calculate the average of the total number of payments made using the most preferred payment method for each product category, where the most preferred payment method in a category is the one with the highest number of payments? " )
