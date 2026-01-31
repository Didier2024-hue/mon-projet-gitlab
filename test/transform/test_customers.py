import pytest
import pandas as pd
import os

@pytest.fixture(scope="module")
def get_df():
    data_dir = os.getenv("DATA_DIR")
    if data_dir == None:
        print("DATA_DIR environment variable not set")
        exit(1)
    df = pd.read_csv(f"{data_dir}/to_ingest/silver/customers.csv")
    return df

def test_duplicated(get_df):
    df = get_df
    df_duplicated = df.groupby(['id', 'modification_date'], as_index=False).size()
    len_duplicated_rows = len(df_duplicated[df_duplicated["size"] > 1])
    assert len_duplicated_rows == 0, f"{len_duplicated_rows} rows are duplicated"

def test_nan(get_df):
    df = get_df
    series_nan = df.isna().sum() * 100 / len(df)
    series_nan_filtered = series_nan[series_nan > 5.0]
    len_series_nan_filtered = len(series_nan_filtered)
    assert len_series_nan_filtered == 0, f"{len_series_nan_filtered} columns contains too much nan values"
