import pandas as pd


def load_csv(file) -> dict:
    df = pd.read_csv(file)
    return {"type": "table", "data": df}
