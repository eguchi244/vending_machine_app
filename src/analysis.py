import pandas as pd

def load_data():
    df = pd.read_csv("vending_machine_log.csv")
    df["detetime"] = pd.to_datetime(df["datetime"])
    return df