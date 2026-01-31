import pytest
import pandas as pd
import os
import psycopg2

load_dir = os.getenv("LOAD_DIR")

postgres_config = {
    'host': os.getenv('POSTGRES_SERVICE_HOST'),
    'user': os.getenv('DATABASE_USER'),
    'database': os.getenv('DATABASE')
}


@pytest.fixture(scope="module")
def get_unset_env_variables():
    unset_env_variables = []
    if load_dir == None:
        unset_env_variables.append("LOAD_DIR")
    for key in postgres_config.keys():
        if postgres_config[key] == None:
            unset_env_variables.append(f"POSTGRES' {key.upper()}")
    if len(unset_env_variables):
        unset_env_var_string = ', '.join(unset_env_variables)
        return unset_env_var_string
    return ""

def connect_psql(config=postgres_config):
    try:
        with psycopg2.connect(**config) as conn:
            print('Connected to the PostgreSQL server.')
            return conn
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)

def test_customer(get_unset_env_variables):
    unset_env_variables = get_unset_env_variables
    assert  unset_env_variables == "", f'{unset_env_variables} environment(s) variable(s) not set'
    df = pd.read_csv(f"{load_dir}/results.csv")
    with connect_psql() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT count(*)
            FROM customer
        ''')
        n_rows_postgres = cursor.fetchone()[0]
        n_rows_df = df[df['table_name'] == 'customer']['n_rows'][0]
        assert n_rows_postgres == n_rows_df, f"Table customer : The number of rows doesn't match"
