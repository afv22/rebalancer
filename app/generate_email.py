import pandas as pd


def generate_email(df: pd.DataFrame) -> str:
    currency_columns = ["current_value", "rebalance_value"]
    percentage_columns = [
        "target_allocation",
        "current_allocation",
        "absolute_difference",
        "relative_difference",
    ]
    integer_columns = ["rebalance_quantity"]

    for col in currency_columns:
        df[col] = df[col].map("${:,.2f}".format)
    for col in percentage_columns:
        df[col] = df[col].map(lambda x: x * 100).map("{:,.1f}%".format)
    for col in integer_columns:
        df[col] = df[col].map(int)

    return df.to_html(justify="end")
