import os
import psycopg2
import pandas as pd
from sqlalchemy import create_engine, table, column
from sqlalchemy.dialects.postgresql import insert
from datetime import datetime
import json

table_customer = table('customer',
    column('id'),
    column('lastname'),
    column('firstname'),
    column('sex'),
    column('modification_date'),
    column('street_number'),
    column('street_name'),
    column('city'),
    column('postcode'),
    column('region')
)

table_product = table('product',
    column('id'),
    column('name'),
    column('categories'),
    column('price'),
    column('weight'),
    column('modification_date')
)

table_order = table('order',
    column('id'),
    column('date_order'),
    column('date_shipping'),
    column('quantity'),
    column('price'),
    column('customer_id'),
    column('product_id')
)

def load_config():
    config = {}
    config['host'] = os.getenv('POSTGRES_SERVICE_HOST')
    config['database'] = os.getenv('DATABASE')
    config['user'] = os.getenv('DATABASE_USER')
    return config

def is_env_variables(data_dir, load_dir, config):
    unset_env_variables = []
    if data_dir == None:
        unset_env_variables.append('DATA_DIR')
    if load_dir == None:
        unset_env_variables.append('LOAD_DIR')
    for key in config.keys():
        if config[key] == None:
            unset_env_variables.append(f"POSTGRES' {key.upper()}")
    if len(unset_env_variables):
        unset_env_var_string = ', '.join(unset_env_variables)
        print(f'{unset_env_var_string} environment(s) variable(s) not set')
        return False
    return True

def connect(config):
    """ Connect to the PostgreSQL database server """
    try:
        with psycopg2.connect(**config) as conn:
            print('Connected to the PostgreSQL server.')
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)

def execute_query_psql(query, config):
    """ Insert data into a table """
    conn_string = 'postgresql://' + config['user'] + '@' + config['host'] + '/' + config['database']    
    try:
        db = create_engine(conn_string)
        with db.begin() as conn:
            res = conn.execute(query)
            return res.rowcount
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

def upsert_customer_to_psql(table_customer, df_customer, df_result):
    dict_customer = [{k: v if pd.notnull(v) else None for k, v in m.items()} for m in df_customer.to_dict(orient='records')]
    insert_stmt = insert(table_customer).values(dict_customer)
    do_update_stmt = insert_stmt.on_conflict_do_update(
        index_elements=[table_customer.c.id, table_customer.c.modification_date],
        set_={
            'id': insert_stmt.excluded.id,
            'firstname': insert_stmt.excluded.firstname,
            'lastname': insert_stmt.excluded.lastname,
            'sex': insert_stmt.excluded.sex,
            'modification_date': insert_stmt.excluded.modification_date,
            'street_number': insert_stmt.excluded.street_number,
            'street_name': insert_stmt.excluded.street_name,
            'city': insert_stmt.excluded.city,
            'postcode': insert_stmt.excluded.postcode,
            'region': insert_stmt.excluded.region
        }
    )
    rowcount = execute_query_psql(do_update_stmt, config)
    print(f'{rowcount} customer rows has been inserted or updated')
    df_result.loc[len(df_result)] = [
        'customer',
        rowcount
    ]

def upsert_product_to_psql(table_product, df_product, df_result):
    dict_product = [{k: v if pd.notnull(v) else None for k, v in m.items()} for m in df_product.to_dict(orient='records')]
    insert_stmt = insert(table_product).values(dict_product)
    do_update_stmt = insert_stmt.on_conflict_do_update(
        index_elements=[table_product.c.id, table_product.c.modification_date],
        set_={
            'id': insert_stmt.excluded.id,
            'name': insert_stmt.excluded.name,
            'categories': insert_stmt.excluded.categories,
            'price': insert_stmt.excluded.price,
            'weight': insert_stmt.excluded.weight,
            'modification_date': insert_stmt.excluded.modification_date
        }
    )
    rowcount = execute_query_psql(do_update_stmt, config)
    print(f'{rowcount} product rows has been inserted or updated')
    df_result.loc[len(df_result)] = [
        'product',
        rowcount
    ]

def get_list_order(filepath_order):
    list_order = []
    with open(filepath_order, 'r') as file_order:
        for line in file_order:
            list_order.append(json.loads(line))
    return list_order

def upsert_order_to_psql(table_order, list_order, df_result):
    insert_stmt = insert(table_order).values(list_order)
    rowcount = execute_query_psql(insert_stmt, config)
    print(f'{rowcount} order rows has been inserted or updated')
    df_result.loc[len(df_result)] = [
        'order',
        rowcount
    ]

if __name__ == '__main__':
    data_dir = os.getenv("DATA_DIR")
    load_dir = os.getenv("LOAD_DIR")
    config = load_config()
    if not is_env_variables(data_dir, load_dir, config):
        exit(1)
    df_customer = pd.read_csv(f'{data_dir}/to_ingest/silver/customers.csv')
    df_product = pd.read_csv(f'{data_dir}/to_ingest/silver/products.csv')
    list_order = get_list_order(f'{data_dir}/to_ingest/silver/orders.json')
    df_result = pd.DataFrame(columns=['table_name', 'n_rows'])
    upsert_customer_to_psql(table_customer, df_customer, df_result)
    upsert_product_to_psql(table_product, df_product, df_result)
    upsert_order_to_psql(table_order, list_order, df_result)
    df_result.to_csv(f'{load_dir}/results.csv', index=False)
