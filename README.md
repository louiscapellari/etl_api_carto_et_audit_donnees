# Workflow ETL simple utilisant l'API CARTO de l'IGN, et audit des données récupérées 
## Objectifs
- Récupérer une couche depuis l'API CARTO de l'IGN (API accessible librement) en python ou via une commande GDAL/OGR en filtrant spatialement les données récupérées et en faisant une historisation des données ; 
- Intégrer automatiquement les données dans une base de données PostgreSQL/PostGIS ;
- Auditer simplement et rapidement et les données récupérées via un script SQL.

## Source des données 
| Fournisseur       | API utilisée  | Lien de l'API | Couche récupérée |
|-------------------|---------------|---------------|------------------|
| **IGN** | API CARTO (REST) | https://apicarto.ign.fr/api/nature/znieff1 | znieff1 |

## Dépendances 
Testé dans un environnement python 3.12.11 généré via Anaconda.
Testé avec PostgreSQL 17.

Liste des librairies python indispensables :
Script GDAL/OGR : 
- GDAL

Script Python : 
- requests
- psycopg2
- shapely

## Instructions 
### GDAL
Script : 
`ogr2ogr -f "PostgreSQL" PG:"host=localhost dbname= user=postgres password=" "https://apicarto.ign.fr/api/nature/znieff1" -nln ign_znieff1 -nlt PROMOTE_TO_MULTI -a_srs EPSG:4326 -t_srs EPSG:2154 -lco GEOMETRY_NAME=geom -overwrite -spat 1.30 49.80 4.30 51.20`
- Créez un environnement python disposant de toutes les librairies mentionnées ci-dessus pour le script GDAL/OGR ;
- Créez une base de données PostgreSQL/PostGIS que vous nommerez comme vous souhaitez ;
- Dans le script GDAL/OGR, renseignez le nom de la base de données `dbname=`, éventuellement le user `user=` et enfin le mot de passe de votre base de données `password=`; 
- Copier/coller le script dans une console exploitant l'environnement python. 

### Python 
- Créez un environnement python disposant de toutes les librairies mentionnées ci-dessus pour le script python ;
- Créez une base de données PostgreSQL/PostGIS que vous nommerez comme vous souhaitez ;
- Dans le script python, renseignez le nom de la base de données, éventuellement le user et enfin le mot de passe de votre base de données ;
- Exécutez le fichier "apiznieff1.py" dans un terminal exploitant l'environnement python la commande "python apiznieff1.py", uniquement lorsque vous êtes placé dans le dossier contenant les scripts, (exemple dans le terminal : cd "chemin du dossier contenant les scripts"). ;
- Le script va exécuter le processus ETL automatiquement jusqu'à sa complétion ;

## Résultats : 
GDAL/OGR : 

Python :

## Améliorations 
- Mapping des champs selon un modèle conceptuel de données 
