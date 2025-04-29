import pandas as pd
from tabulate import tabulate

def format_results(rows, columns):
    if not rows:
        return {"table": "No results returned", "json": []}

    df = pd.DataFrame(rows, columns=columns)
    
    for col in df.select_dtypes(include=['datetime']).columns:
        df[col] = df[col].dt.strftime('%Y-%m-%d %H:%M:%S')

    for col in df.select_dtypes(include=['number']).columns:
        df[col] = df[col].apply(lambda x: f"{x:.2f}" if pd.notnull(x) else x)

    table = tabulate(df, headers='keys', tablefmt='psql', showindex=False)
    json_result = df.to_dict(orient='records')

    return {"table": table, "json": json_result}
