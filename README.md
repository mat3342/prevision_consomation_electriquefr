Il s'agit du début d'un projet qui à pour objectif final de prédire la consomation
éléctrique française heure par heure.
Pour ca nous allons récupérer les données depuis éco2mixnational consolidé et défitif (rte) ainsi que meteo historical weather api
Nous allons netoyé ce donnée puis nous allons entrainé différent modèle prédictifs afin de pouvoir ensuite l'utilisé sur les données actuelles
Enfin Nous créerons un interface graphique

===============================================
Les donnée
===============================================

Les données brut:
- Données énergétique de la france:
    téléchargé depuis https://odre.opendatasoft.com
    Elles sont aux format CSV:
        separateur: ;
        header : perimetre;nature;date;heure;date_heure;consommation
        pas : 1/4 heure

- Données météo de 22 plus grandes métropoles françaises:
    Téléchargé depuis le site https://open-meteo.com, ces données sont issus du model "era5" (representant une zone de 25km par 25km) il y a un fichier par ville (meteo{nom de la ville}.csv)
    format csv:
        separateur : ;
        header : date;temperature_2m;wind_speed_10m;cloud_cover;rain
        pas : heure

