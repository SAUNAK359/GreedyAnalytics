def mask_pii(df):
    for col in df.columns:
        if "email" in col.lower():
            df[col] = "***MASKED***"
    return df
