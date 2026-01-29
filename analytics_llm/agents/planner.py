from typing import Dict, Any


class PlannerAgent:
    def plan(self, question: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        columns = schema.get("columns", [])
        date_cols = [c for c in columns if schema.get("types", {}).get(c, "").startswith("datetime")]
        numeric_cols = [c for c in columns if schema.get("types", {}).get(c, "").startswith("float") or schema.get("types", {}).get(c, "").startswith("int")]

        x = date_cols[0] if date_cols else (columns[0] if columns else None)
        y = numeric_cols[0] if numeric_cols else None

        return {
            "question": question,
            "operation": "summary",
            "x": x,
            "y": y,
            "chart_type": "line" if x and y else "table",
            "metrics": [y] if y else [],
        }
