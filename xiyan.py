from sqlalchemy import create_engine
from schema_engine import SchemaEngine


def mschema():
    """
    阿里析言中组织Schema的方式
    :return:
    """
    db_engine = create_engine(f'sqlite:///ecommerce.db')
    schema_engine = SchemaEngine(engine=db_engine, db_name='ecommerce.db')
    mschema = schema_engine.mschema
    mschema_str = mschema.to_mschema()
    print(mschema_str)
    return mschema_str

if __name__ == '__main__':
    mschema()
