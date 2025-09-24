import pandas as pd
from tabulate import tabulate
import numpy as np
from decimal import Decimal

def format_results(rows, columns):
    if not rows:
        return {"table": "No results returned", "json": []}

    df = pd.DataFrame(rows, columns=columns)

    for col in df.columns:
        if df[col].apply(lambda x: isinstance(x, Decimal)).any():
            df[col] = df[col].apply(lambda x: float(x) if pd.notnull(x) else x)

    for col in df.select_dtypes(include=['datetime']).columns:
        df[col] = df[col].dt.strftime('%Y-%m-%d %H:%M:%S')

    for col in df.columns:
        if df[col].apply(lambda x: isinstance(x, pd.Timedelta)).any():
            df[col] = df[col].apply(lambda x: x.total_seconds() / 86400 if pd.notnull(x) else x)

    for col in df.select_dtypes(include=[np.number]).columns:
        if 'id' not in col.lower():  
            df[col] = df[col].apply(lambda x: f"{x:.2f}" if pd.notnull(x) else x)
        else:
            df[col] = df[col].apply(lambda x: int(x) if pd.notnull(x) else x)

    table = tabulate(df, headers='keys', tablefmt='psql', showindex=False)
    json_result = df.to_dict(orient='records')

    return {"table": table, "json": json_result}
