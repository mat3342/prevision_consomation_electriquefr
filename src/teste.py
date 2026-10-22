import pandas as pd

DATASET="eco2mix-national-cons-def"

df = pd.read_csv(f"./data/raw/{DATASET}.csv", sep=";", parse_dates=["date_heure"])
df = df.dropna(subset=["consommation"]).sort_values("date_heure")
print(df.shape)
print(df.head())
