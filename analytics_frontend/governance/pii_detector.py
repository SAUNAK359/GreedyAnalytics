import re
import pandas as pd
from typing import Dict, Any

EMAIL_RE = re.compile(r"[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(r"\+?\d[\d\s\-]{7,}\d")


def detect_pii(df: pd.DataFrame) -> Dict[str, Any]:
    findings = {}
    for col in df.columns:
        sample = df[col].astype(str).head(200).tolist()
        hits = []
        for value in sample:
            if EMAIL_RE.search(value) or PHONE_RE.search(value):
                hits.append(value)
        if hits:
            findings[col] = {
                "samples": hits[:5],
                "count": len(hits),
            }
    return findings
