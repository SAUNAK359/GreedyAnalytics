import pandas as pd
from typing import Dict, Any


def profile_dataset(df: pd.DataFrame) -> Dict[str, Any]:
    profile = {
        "nulls": df.isna().sum().to_dict(),
        "cardinality": df.nunique().to_dict(),
        "rows": len(df),
        "columns": len(df.columns),
    }
    return profile
