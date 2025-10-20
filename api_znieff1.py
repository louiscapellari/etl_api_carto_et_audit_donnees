import os, json, sys
import requests
import psycopg2
from psycopg2.extras import execute_values
from shapely.geometry import shape, box


url_api    = os.environ.get("IGN_API_URL", "https://apicarto.ign.fr/api/nature/znieff1")
geom_filtre = os.environ.get("IGN_API_GEOM")                    
bbox_spatiale = os.environ.get("IGN_SPAT_BBOX", "1.30,49.80,4.30,51.20")  

pg_host = os.environ.get("PGHOST", "localhost")
pg_port = int(os.environ.get("PGPORT", "5432"))
pg_bdd  = os.environ.get("PGDATABASE", "") # À renseigner
pg_user = os.environ.get("PGUSER", "postgres") # À éventuellement modifier 
pg_mdp  = os.environ.get("PGPASSWORD", "") # À renseigner

nom_table   = os.environ.get("TARGET_TABLE", "ign_znieff1")
srid_cible  = 2154


def get_features(url, filtre_geom_texte):
    params = {}
    if filtre_geom_texte:
        params["geom"] = filtre_geom_texte
    r = requests.get(url, params=params, timeout=120)
    r.raise_for_status()
    data = r.json()
    if isinstance(data, dict) and data.get("type") == "FeatureCollection":
        return data.get("features", [])
    if isinstance(data, list):
        return data
    raise RuntimeError("Réponse inattendue de l'API")


def main():
    try:
        features = get_features(url_api, geom_filtre)
        print(f"{len(features)} entités reçues")

        xmin, ymin, xmax, ymax = [float(x) for x in bbox_spatiale.replace(";", ",").split(",")]
        emprise = box(xmin, ymin, xmax, ymax)
        filtre_local = None
        if geom_filtre:
            try:
                filtre_local = shape(json.loads(geom_filtre))
            except Exception:
                filtre_local = None

        conn = psycopg2.connect(host=pg_host, port=pg_port, dbname=pg_bdd, user=pg_user, password=pg_mdp)
        conn.autocommit = False

        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS {nom_table} (
                    id SERIAL PRIMARY KEY,
                    feature_id TEXT,
                    properties JSONB NOT NULL,
                    geom geometry(Geometry, {srid_cible})
                );
            """)
            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS {nom_table}_histo (
                    installed_rank SERIAL PRIMARY KEY,
                    version TEXT NOT NULL,
                    description TEXT NOT NULL,
                    date_ajout timestamptz NOT NULL DEFAULT now(),
                    success BOOLEAN NOT NULL
                );
            """)
            cur.execute(f"TRUNCATE TABLE {nom_table};")

            lignes = []
            for f in features:
                props = f.get("properties") or {}
                fid = f.get("id") or props.get("id") or props.get("identifiant")
                g = f.get("geometry")
                if not g:
                    lignes.append((fid, json.dumps(props, ensure_ascii=False), None, None))
                    continue

                geom_obj = shape(g)

                if not geom_obj.intersects(emprise):
                    continue
                if filtre_local is not None and not geom_obj.intersects(filtre_local):
                    continue

                wkb = geom_obj.wkb
                lignes.append((fid, json.dumps(props, ensure_ascii=False), wkb, wkb))

            if lignes:
                execute_values(
                    cur,
                    f"INSERT INTO {nom_table} (feature_id, properties, geom) VALUES %s",
                    lignes,
                    template=f"""
                    (%s, %s,
                        CASE
                          WHEN %s IS NULL THEN NULL
                          ELSE ST_Transform(ST_SetSRID(ST_GeomFromWKB(%s), 4326), {srid_cible})
                        END
                    )
                    """,
                    page_size=5000
                )

            cur.execute(
                f"INSERT INTO {nom_table}_histo (version, description, success) VALUES (%s, %s, %s)",
                ("1.0", "couche znieff1 issue de l'API CARTO IGN", True)
            )

        conn.commit()
        print("Import terminé")

    except Exception as e:
        print(f"Erreur : {e}", file=sys.stderr)
        try:
            conn.rollback()
        except Exception:
            pass
        try:
            with psycopg2.connect(host=pg_host, port=pg_port, dbname=pg_bdd, user=pg_user, password=pg_mdp) as c2:
                c2.autocommit = True
                with c2.cursor() as cur2:
                    cur2.execute(f"""
                        CREATE TABLE IF NOT EXISTS {nom_table}_histo (
                            installed_rank SERIAL PRIMARY KEY,
                            version TEXT NOT NULL,
                            description TEXT NOT NULL,
                            date_ajout timestamptz NOT NULL DEFAULT now(),
                            success BOOLEAN NOT NULL
                        );
                    """)
                    cur2.execute(
                        f"INSERT INTO {nom_table}_histo (version, description, success) VALUES (%s, %s, %s)",
                        ("1.0", "couche znieff1 issue de l'API CARTO IGN", False)
                    )
        except Exception:
            pass
        sys.exit(1)
    finally:
        try:
            conn.close()
        except Exception:
            pass

if __name__ == "__main__":
    main()
