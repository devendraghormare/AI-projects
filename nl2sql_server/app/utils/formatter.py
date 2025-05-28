import pandas as pd
from tabulate import tabulate
import numpy as np

def format_results(rows, columns):
    if not rows:
        return {"table": "No results returned", "json": []}

    df = pd.DataFrame(rows, columns=columns)

    # Convert datetime columns to string
    for col in df.select_dtypes(include=['datetime']).columns:
        df[col] = df[col].dt.strftime('%Y-%m-%d %H:%M:%S')

    # Convert timedelta to number of days (float)
    for col in df.columns:
        if df[col].apply(lambda x: isinstance(x, pd.Timedelta)).any():
            df[col] = df[col].apply(lambda x: x.total_seconds() / 86400 if pd.notnull(x) else x)

    # Format numeric columns to 2 decimal places
    for col in df.select_dtypes(include=[np.number]).columns:
        df[col] = df[col].apply(lambda x: f"{x:.2f}" if pd.notnull(x) else x)

    table = tabulate(df, headers='keys', tablefmt='psql', showindex=False)
    json_result = df.to_dict(orient='records')

    return {"table": table, "json": json_result}
