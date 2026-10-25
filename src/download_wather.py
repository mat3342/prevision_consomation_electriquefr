import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry
from pathlib import Path
from datetime import date, timedelta,datetime
from dateutil.relativedelta import relativedelta
import time
from openmeteo_requests.Client import OpenMeteoRequestsError


RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
FICHIER = RAW_DIR / "meteo_era5_metropoles.csv"





METROPOLES = [
    # nom,              latitude, longitude, population (en vigueur au 1er janvier 2025, millésimée 2022)
    ("Paris",            48.8566,  2.3522, 7_163_419),
    ("Marseille",        43.2965,  5.3698, 1_944_405),
    ("Lyon",             45.7640,  4.8357, 1_433_613),  # Insee, population municipale
    ("Lille",            50.6292,  3.0573, 1_204_796),
    ("Bordeaux",         44.8378, -0.5792,   854_949),
    ("Toulouse",         43.6047,  1.4442,   842_175),
    ("Nantes",           47.2184, -1.5536,   695_303),
    ("Nice",             43.7102,  7.2620,   574_284),
    ("Montpellier",      43.6108,  3.8767,   523_109),
    ("Strasbourg",       48.5734,  7.7521,   522_670),
    ("Rouen",            49.4432,  1.0999,   507_654),
    ("Rennes",           48.1173, -1.6778,   483_199),
    ("Grenoble",         45.1885,  5.7245,   455_436),
    ("Toulon",           43.1242,  5.9280,   455_118),
    ("Saint-Étienne",    45.4397,  4.3872,   412_411),
    ("Tours",            47.3941,  0.6848,   304_421),
    ("Clermont-Ferrand", 45.7772,  3.0870,   302_259),
    ("Orléans",          47.9030,  1.9093,   299_552),
    ("Dijon",            47.3220,  5.0415,   263_672),
    ("Nancy",            48.6921,  6.1844,   262_233),
    ("Metz",             49.1193,  6.1757,   234_112),
    ("Brest",            48.3904, -4.4861,   217_444),
]

def request(debut:str,fin:str,ville:list):
    latitudes   = ",".join(str(m[1]) for m in ville)
    longitudes  = ",".join(str(m[2]) for m in ville)
    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": latitudes,
        "longitude": longitudes,
        "start_date": debut,
        "end_date": fin,
        "hourly": "temperature_2m,wind_speed_10m,cloud_cover,rain",
        "timezone": "GMT",
        "models": "era5"
    }
    responses = openmeteo.weather_api(url, params = params)
    return responses

def attendre(secondes: int, raison: str) -> None:
    """Affiche un compte à rebours pendant l'attente."""
    print(f"\n{raison}")
    for reste in range(secondes, 0, -1):
        print(f"\r  reprise dans {reste:4d} s...", end="", flush=True)
        time.sleep(1)
    print("\r  reprise.                    ")


def request_avec_attente(debut, fin, villes, essais_max=10):
    """Appelle request(), et attend puis réessaie si une limite de l'API est atteinte."""
    for essai in range(1, essais_max + 1):
        try:
            return request(debut, fin, villes)

        except OpenMeteoRequestsError as e:
            message = str(e)

            if "Minutely" in message:
                attendre(65, "Limite par minute atteinte.")

            elif "Hourly" in message:
                maintenant = datetime.now()
                secondes = (60 - maintenant.minute) * 60 - maintenant.second + 30
                attendre(secondes, "Limite par heure atteinte, attente du début de l'heure suivante.")

            elif "Daily" in message:
                raise SystemExit(
                    "Limite par jour atteinte. Relance le script demain : "
                    "il reprendra là où il s'est arrêté."
                ) from e

            else:
                raise          # autre erreur (paramètre invalide, panne...) : on ne la masque pas

    raise RuntimeError(f"Abandon après {essais_max} essais pour {debut} → {fin}.")






def min_date_in_metrop_file()->str:
    #On veut la plus ancienne dates parimis les dates les plus recenttes de chaque fichier


    debut="2012-01-01"#date la plus ancienne possible
    maxi=[]
    for i in range(len(METROPOLES)):
        if Path(f"{RAW_DIR}/meteo{METROPOLES[i][0]}.csv").resolve().exists():
            df_temp = pd.read_csv(f"{RAW_DIR}/meteo{METROPOLES[i][0]}.csv", sep=";",usecols=["date"], parse_dates=["date"])
            dates = df_temp["date"]
            if dates.empty:
                return debut          # si jamais le fichier ne contient pas de dates
            dates=dates.max().strftime("%Y-%m-%d")
            maxi.append(dates)
        else:
            #si une ville n'exist pas on veut donc ces dates depuis le début
            return debut 
   
    return min(maxi)

def request_y_by_y (fin:str,debut="2012-01-01") :
    d=max(debut,min_date_in_metrop_file())
    d=date.fromisoformat(d)
    d=d+relativedelta(days=1)
    fin=date.fromisoformat(fin)
    while d < fin:
        fin_annee = min(date(d.year, 12, 31), fin)
        responses=request_avec_attente(d,fin_annee,METROPOLES)

        

        for i in range(len(METROPOLES)):
            response=responses[i]
            hourly = response.Hourly()
            data = {
            "date": pd.date_range(
                start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
                end =  pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
                freq = pd.Timedelta(seconds = hourly.Interval()),
                inclusive = "left"
                )
            }
            for x,var in enumerate(["temperature_2m","wind_speed_10m","cloud_cover","rain"]):
                data[var]=hourly.Variables(x).ValuesAsNumpy()
            df=pd.DataFrame(data = data)
            if Path(f"{RAW_DIR}/meteo{METROPOLES[i][0]}.csv").resolve().exists():
                h=False
                m="a"
            else:
                h=True
                m="w"
                
            df.to_csv(f"{RAW_DIR}/meteo{METROPOLES[i][0]}.csv",sep=";",mode=m,header=h, index=False)

        print(f"Année {d.year} a bien été télécharge")

        d = fin_annee + relativedelta(days=1) 


def main():
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)



    auj=date.today()
    fin = (auj - timedelta(days=6)).isoformat()

    request_y_by_y(fin)
    print("Toutesles données météo ont bien été téléchargé")






