from typing import Dict, Any
import pandas as pd


class ExecutorAgent:
    def execute(self, plan: Dict[str, Any], df: pd.DataFrame | None) -> Dict[str, Any]:
        if df is None or df.empty:
            return {"data": None, "error": "No data loaded"}

        x = plan.get("x")
        y = plan.get("y")

        if x and y and x in df.columns and y in df.columns:
            result = df[[x, y]].copy()
            return {"data": result, "error": None}

        return {"data": df.head(200), "error": None}
