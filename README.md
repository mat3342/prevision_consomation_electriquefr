Il s'agit du début d'un projet qui à pour objectif final de prédire la consomation
éléctrique française heure par heure.
Pour ca nous allons récupérer les données depuis éco2mixnational consolidé et défitif (rte) ainsi que meteo historical weather api
Nous allons netoyé ce donnée puis nous allons entrainé différent modèle prédictifs afin de pouvoir ensuite l'utilisé sur les données actuelles
Enfin Nous créerons un interface graphique

===============================================
# Les donnée
===============================================

## les données brutes
Les données brutes sont stockées dans `data/raw/`.

### 1. Consommation électrique française (éCO2mix)

- **Source :** [ODRÉ](https://odre.opendatasoft.com) (RTE), jeu de données `eco2mix-national-cons-def`
- **Fichier :** `eco2mix-national-cons-def.csv`
- **Format :** CSV, séparateur `;`
- **Pas de temps :** 15 minutes
- **Période :** depuis le 1er janvier 2012
- **Périmètre :** France métropolitaine continentale (hors Corse)

| Colonne        | Type                    | Unité | Description |
|----------------|-------------------------|-------|-------------|
| `perimetre`    | texte                   | —     | Zone géographique (`France`) |
| `nature`       | texte                   | —     | Statut des données (consolidées / définitives) |
| `date`         | texte (`AAAA-MM-JJ`)    | —     | Date en **heure légale française** (avec changement d'heure) |
| `heure`        | texte (`HH:MM`)         | —     | Heure en **heure légale française** (avec changement d'heure) |
| `date_heure`   | date-heure ISO 8601     | —     | Horodatage en **UTC** (ex. `2024-03-15T13:30:00+00:00`) |
| `consommation` | entier                  | MW    | Puissance moyenne consommée sur le pas de temps |

> ℹ️ Selon la période, certaines lignes ont une `consommation` vide : elles sont à filtrer à la lecture.

### 2. Météo des 22 plus grandes métropoles françaises

- **Source :** [Open-Meteo](https://open-meteo.com), API *Historical Weather*, modèle `era5`
- **Fichiers :** un fichier par ville, `meteo{Ville}.csv` (ex. `meteoParis.csv`)
- **Format :** CSV, séparateur `;`
- **Pas de temps :** 1 heure
- **Période :** depuis le 1er janvier 2012 (ERA5 est publié avec environ 5 jours de retard)
- **Résolution spatiale :** maille d'environ 25 km × 25 km (0,25°) centrée près du centre de chaque ville

| Colonne          | Type                | Unité | Description |
|------------------|---------------------|-------|-------------|
| `date`           | date-heure ISO 8601 | —     | Horodatage en **UTC** |
| `temperature_2m` | décimal             | °C    | Température de l'air à 2 m, **instantanée** |
| `wind_speed_10m` | décimal             | km/h  | Vitesse du vent à 10 m, **instantanée** |
| `cloud_cover`    | décimal (0 – 100)   | %     | Couverture nuageuse totale, **instantanée** |
| `rain`           | décimal             | mm    | Pluie liquide **cumulée sur l'heure précédente** (hors neige) |



