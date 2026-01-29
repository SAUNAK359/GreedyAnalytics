import pandas as pd


def load_parquet(file) -> dict:
    df = pd.read_parquet(file)
    return {"type": "table", "data": df}
