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


def run_sql_query(query: str, db_path='ecommerce.db'):
    """
    执行传入的 SQL 查询，并以美观表格格式打印结果。
    :param db_path: SQLite 数据库文件路径
    :param query: 要执行的 SELECT 查询语句
    """
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        if rows:
            res = tabulate(rows, headers=column_names, tablefmt="grid", stralign="center")
            print(res)
            return res
        else:
            print("查询成功，但无返回结果。")

    except sqlite3.Error as e:
        print(f"SQL 执行错误：{e}")
        return e
    finally:
        conn.close()


def extract_schema_prompt(db_path='ecommerce.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    prompt_lines = []
    # 获取所有表名
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = cursor.fetchall()

    for (table_name,) in tables:
        prompt_lines.append(f"【{table_name}】")
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()  # (cid, name, type, notnull, dflt_value, pk)

        for col in columns:
            name, col_type, notnull, dflt, pk = col[1], col[2], col[3], col[4], col[5]
            desc = f"{name}: {col_type}"
            prompt_lines.append("  - " + desc)

        prompt_lines.append("")

    conn.close()
    return "\n".join(prompt_lines)


def gen_system_prompt(prompt: str):
    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", """
你是一个SQL专家，请根据提供的表结构信息和查询需求，来生成可执行的sqlite支持的sql查询语句，你只能回复可执行的SQL内容,
生成的sql放在<SQL>标签内部

A: 查询用户的数量
Q: <SQL>select count(*) from users</SQL>

"""),
            ("human", """
【数据库的结构】
{schema}

【查询需求】
{input} """),
        ]
    )
    schema = extract_schema_prompt()
    prompt_value = prompt_template.invoke({"input": prompt, "schema": schema})

    print(prompt_value.to_string())

    llm = get_llm()
    res = llm.invoke(prompt_value).content
    return res.replace("<SQL>", "").replace("</SQL>", "")


if __name__ == "__main__":
    

    sql = gen_system_prompt(
        "在2016、2017和2018年中,全年'已送达'订单数量最少的那一年,该年'已送达'订单数量最多的月份的订单量是多少?")
    print(sql)
    run_sql_query(sql)
