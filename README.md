# Workflow ETL simple utilisant l'API CARTO de l'IGN, et audit des données récupérées 
## Objectifs
- Récupérer une couche depuis l'API CARTO de l'IGN (API accessible librement) en python ou via une commande OGR (GDAL) en filtrant spatialement, reprojetant les données récupérées (4326 vers 2154) et en faisant une historisation des données ; 
- Intégrer automatiquement les données dans une base de données PostgreSQL/PostGIS ;
- Auditer simplement et rapidement et les données récupérées via un script SQL.

## Source des données 
| Fournisseur       | API utilisée  | Lien de l'API | Couche récupérée |
|-------------------|---------------|---------------|------------------|
| **IGN** | API CARTO (REST) | https://apicarto.ign.fr/api/nature/znieff1 | znieff1 |

## Dépendances 
Testé dans un environnement python 3.12.11 généré via Anaconda. </br>
Testé avec PostgreSQL 17.

Liste des librairies python indispensables :</br>
Commande OGR :</br> 
- GDAL

Script Python : 
- requests
- psycopg2
- shapely

## Instructions 

Vous pouvez choisir d'éxécuter soit la commande OGR, soit le script python pour charger les données dans la base de données. </br>
Une fois l'un ou l'autre des scripts exécuté, vous pouvez passer à la réalisation de l'audit des données. 

### OGR (GDAL) :</br>
Commande :</br> 
`ogr2ogr -f "PostgreSQL" PG:"host=localhost dbname= user=postgres password=" "https://apicarto.ign.fr/api/nature/znieff1" -nln ign_znieff1 -nlt PROMOTE_TO_MULTI -a_srs EPSG:4326 -t_srs EPSG:2154 -lco GEOMETRY_NAME=geom -overwrite -spat 1.30 49.80 4.30 51.20`
- Créez un environnement python disposant de toutes les librairies mentionnées ci-dessus pour la commande OGR;
- Créez une base de données PostgreSQL/PostGIS que vous nommerez comme vous souhaitez ;
- Dans la commande OGR, renseignez le nom de la base de données `dbname=`, éventuellement le user `user=` et enfin le mot de passe de votre base de données `password=`; 
- Copier/coller le script dans une console exploitant l'environnement python.
- Le script va exécuter le processus ETL automatiquement jusqu'à sa complétion ;
- Une fois terminé, la base de données sera alimentée, les données seront stockées dans le schéma "public" par défaut, car dans le cadre de ce script, aucun schéma n'a été crée ou renseigné;
- Les données récupérées sont grossièrement filtrées sur le nord de la France depuis le script, et reprojetées en 2154;
- La commande OGR ne génère pas d'historisation dans notre cas. 

### Python :
- Télécharger le script `apiznieff1.py`
- Créez un environnement python disposant de toutes les librairies mentionnées ci-dessus pour le script python ;
- Créez une base de données PostgreSQL/PostGIS que vous nommerez comme vous souhaitez ;
- Dans le script python, renseignez le nom de la base de données, éventuellement le user et enfin le mot de passe de votre base de données ;
- Exécutez le fichier `apiznieff1.py` dans un terminal exploitant l'environnement python la commande `python apiznieff1.py`, uniquement lorsque vous êtes placé dans le dossier contenant les scripts, (exemple dans le terminal : `cd "chemin du dossier contenant le script"` une fois placé dans le dossier `python apiznieff1.py`). ;
- Le script va exécuter le processus ETL automatiquement jusqu'à sa complétion ;
- Une fois terminé, la base de données sera alimentée, les données seront stockées dans le schéma "public" par défaut, car dans le cadre de ce script, aucun schéma n'a été crée ou renseigné;
- Les données récupérées sont grossièrement filtrées sur le nord de la France depuis le script, et reprojetées en 2154 ;
- Le script python va créer une seconde table `ign_znieff1_histo` qui renseigne certaines informations d'import (version, timestamp...). 

### Audit des données :
- Exécutez l'un au l'autre des scripts au préalable ;
- Depuis votre SGBD (PG Admin, Dbeaver...), exécutez le script SQL d'audit des données ;
- Un tableau de résultat sera retourné en fin de script. 


## Résultats : 
### OGR (GDAL) : 
Exécution du script dans la console python :</br> 
<img width="694" height="38" alt="commande_ogr" src="https://github.com/user-attachments/assets/206865b9-8f52-4821-9506-0afd09b525d0" /></br>
Tables dans la base de données :</br> 
<img width="196" height="60" alt="ogr_bdd" src="https://github.com/user-attachments/assets/b476b836-1a86-491b-a644-a2b46420991a" /></br>
Résultat sur QGIS :</br> 
<img width="958" height="443" alt="resultat_ogr" src="https://github.com/user-attachments/assets/d315d57b-1700-403b-9fff-fa8cd36fe773" /></br>

### Python :
Exécution du script dans la console python :</br> 
<img width="656" height="36" alt="load_etl" src="https://github.com/user-attachments/assets/95c030e5-08bf-4009-bd62-3e1614224aa1" /></br>
Bonne complétion du script :</br> 
<img width="140" height="28" alt="completion_script" src="https://github.com/user-attachments/assets/ebee68be-892f-4154-81a6-10492d11e9a0" /></br>
Tables dans la base de données :</br> 
<img width="283" height="59" alt="table_en_bdd" src="https://github.com/user-attachments/assets/25a53a98-c989-4096-8663-f7ad5e1c4849" /></br>
Table d'historisation dans la base de données :</br> 
<img width="549" height="88" alt="image" src="https://github.com/user-attachments/assets/b57f4711-f1b8-4e3c-a4f4-04bd327bc277" /></br>
Résultat sur QGIS :</br> 
<img width="956" height="416" alt="resultat_script_python" src="https://github.com/user-attachments/assets/5a7a938b-309b-4ac4-85ed-23887fe58bf5" /></br>

### Audit des données : 
Exécution du script (query tool de PG Admin dans notre cas) :</br>
<img width="439" height="260" alt="audit_bdd" src="https://github.com/user-attachments/assets/b0722091-d9af-4a60-a227-bc4de08cda54" /></br>

## Améliorations 
- Créer un schéma particulier pour accueillir les données (comme dans le projet etl_vc) ;
- Mapping des champs selon un modèle conceptuel de données.
