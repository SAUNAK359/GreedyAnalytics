import pandas as pd


def load_excel(file) -> dict:
    df = pd.read_excel(file)
    return {"type": "table", "data": df}
