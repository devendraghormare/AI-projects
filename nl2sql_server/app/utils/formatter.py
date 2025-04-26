import pandas as pd
from tabulate import tabulate

def format_results(rows, columns):
    df = pd.DataFrame(rows, columns=columns)
    table = tabulate(df, headers='keys', tablefmt='psql', showindex=False)
    json_result = df.to_dict(orient='records')
    return {"table": table, "json": json_result}