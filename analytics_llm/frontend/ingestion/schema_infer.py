import pandas as pd
from typing import Dict, Any


def infer_schema(df: pd.DataFrame) -> Dict[str, Any]:
    types = {col: str(dtype) for col, dtype in df.dtypes.items()}
    return {
        "columns": list(df.columns),
        "types": types,
    }
