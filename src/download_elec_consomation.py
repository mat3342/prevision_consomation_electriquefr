import requests
from pathlib import Path 
import pandas as pd
from io import StringIO


BASE = "https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets"
DATASET = "eco2mix-national-cons-def"


if Path(f"./data/raw/{DATASET}.csv").exists():
    df = pd.read_csv(f"./data/raw/{DATASET}.csv", sep=";", parse_dates=["date_heure"])
    derniere = df["date_heure"].max()
    date=derniere.isoformat()
else:
    date='2012-01-01'



url = f"{BASE}/{DATASET}/exports/csv"

params = {
    "delimiter": ";",
    # Optionnel : filtrer une période (syntaxe ODSQL)
    "where": f"date_heure > '{date}'" ,
    # Optionnel : limiter les colonnes
    "select": "perimetre,nature,date,heure,date_heure,consommation",
}

with requests.get(url, params=params, stream=True, timeout=300) as r:
    r.raise_for_status()
    with open(f"./data/raw/{DATASET}.csv.tmp", "wb") as f:
        for chunk in r.iter_content(chunk_size=1 << 20):
            f.write(chunk)

nouvelles = pd.read_csv(f"./data/raw/{DATASET}.csv.tmp", sep=";", parse_dates=["date_heure"])
nouvelles = nouvelles.sort_values("date_heure")   # ordre chronologique avant ajout

if not nouvelles.empty:
    if date =='2012-01-01':
        h=True
    else:
        h=False


    colonnes = pd.read_csv(f"./data/raw/{DATASET}.csv.tmp", sep=";", nrows=0).columns
    nouvelles[colonnes].to_csv(f"./data/raw/{DATASET}.csv", mode="a", header=h, index=False, sep=";")
    print(f"{len(nouvelles)} lignes ajoutées")

for f in Path("./data/raw/").glob("*.tmp"):
    f.unlink()
