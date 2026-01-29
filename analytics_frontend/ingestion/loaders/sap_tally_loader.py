import pandas as pd


def load_sap_tally(file) -> dict:
    df = pd.read_csv(file)
    return {"type": "table", "data": df}
