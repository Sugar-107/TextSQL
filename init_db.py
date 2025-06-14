import json
import os
import sqlite3


def load_data(conn, file_path='data/schema.sql', db_path='ecommerce.db'):
    # 读取 JSON 文件
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 获取表名和字段信息
    table_name = data['table_name']
    columns = data['column_names']
    types = data['column_types']
    rows = data['sample_rows']

    # 拼接建表 SQL
    create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} (\n"
    create_table_sql += ",\n".join([
        f"    {col} {col_type}" for col, col_type in zip(columns, types)
    ])
    create_table_sql += "\n);"

    # 拼接插入 SQL
    insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['?'] * len(columns))})"

    cursor = conn.cursor()

    # 执行建表
    cursor.execute(create_table_sql)

    # 插入数据
    for row in rows:
        values = [row.get(col, None) for col in columns]
        cursor.execute(insert_sql, values)

    print(f"数据成功写入 SQLite 数据库中的表：{table_name}")


def exec_sql_file(conn, filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        sql_script = f.read()
    conn.executescript(sql_script)


def load_db(schema_path='data/schema.sql', db_path='ecommerce.db'):
    # 删除旧数据库文件（可选）
    if os.path.exists(db_path):
        os.remove(db_path)

    # 创建数据库连接
    conn = sqlite3.connect(db_path)

    # 执行建表和初始化数据脚本
    exec_sql_file(conn, schema_path)

    load_data(conn, "data/customers.json")
    load_data(conn, "data/geolocation.json")
    load_data(conn, "data/leads_closed.json")
    load_data(conn, "data/leads_qualified.json")
    load_data(conn, "data/order_items.json")
    load_data(conn, "data/order_payments.json")
    load_data(conn, "data/order_reviews.json")
    load_data(conn, "data/orders.json")
    load_data(conn, "data/product_category_name_translation.json")
    load_data(conn, "data/products.json")
    load_data(conn, "data/sellers.json")

    # 提交并关闭连接
    conn.commit()
    conn.close()
    print(f"数据库初始化完成，包含结构和示例数据，文件：{db_path}")




if __name__ == '__main__':
    load_db()
