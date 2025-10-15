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

## Scripts 
`ogr2ogr -f "PostgreSQL" PG:"host=localhost dbname=etl_vc user=postgres password=" "https://apicarto.ign.fr/api/nature/znieff1" -nln ign_znieff1 -nlt PROMOTE_TO_MULTI -a_srs EPSG:4326 -t_srs EPSG:2154 -lco GEOMETRY_NAME=geom -overwrite -spat 1.30 49.80 4.30 51.20`

## Utilisation 

## Améliorations 
- Mapping des champs selon un modèle conceptuel de données 
