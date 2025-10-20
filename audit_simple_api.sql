WITH
vol AS (
  SELECT 1 AS ordre,
         'Volumétrie' AS "Catégories et champs",
         COUNT(*)::text AS valeur,
         'Nombre de lignes' AS information
  FROM public.ign_znieff1
),
srid_decl AS (
  SELECT 2 AS ordre,
         'SRID déclaré' AS "Catégories et champs",
         CASE WHEN Find_SRID('public','ign_znieff1','geom') = 0
              THEN 'inconnu' ELSE Find_SRID('public','ign_znieff1','geom')::text END AS valeur,
         NULL::text AS information
),
geom_null AS (
  SELECT 3 AS ordre,
         'Géométries NULL' AS "Catégories et champs",
         SUM(CASE WHEN geom IS NULL THEN 1 ELSE 0 END)::text AS valeur,
         'Présence de valeurs NULL dans la géométrie' AS information
  FROM public.ign_znieff1
),
srid_diff AS (
  SELECT 4 AS ordre,
         'SRID différent du SRID attendu' AS "Catégories et champs",
         SUM(CASE WHEN geom IS NOT NULL AND ST_SRID(geom) <> 2154 THEN 1 ELSE 0 END)::text AS valeur,
         'SRID attendu = 2154' AS information
  FROM public.ign_znieff1
),
invalides AS (
  SELECT 5 AS ordre,
         'Géométries invalides' AS "Catégories et champs",
         COUNT(*)::text AS valeur,
         '=> ST_MakeValid' AS information
  FROM public.ign_znieff1
  WHERE geom IS NOT NULL AND NOT ST_IsValid(geom)
),
doublons AS (
  SELECT 6 AS ordre,
         'Doublons géométriques' AS "Catégories et champs",
         COALESCE(SUM(c - 1), 0)::text AS valeur,
         'Recensement de doublons de géométrie potentiel' AS information
  FROM (
    SELECT md5(ST_AsBinary(geom)) AS h, COUNT(*) AS c
    FROM public.ign_znieff1
    WHERE geom IS NOT NULL
    GROUP BY md5(ST_AsBinary(geom))
    HAVING COUNT(*) > 1
  ) t
),
remplissage AS (
  SELECT 100 AS ordre,
         key::text AS "Catégories et champs",
         (CASE WHEN COUNT(*)=0 THEN 0
               ELSE ROUND(100.0 * SUM(CASE WHEN value = 'null'::jsonb THEN 0 ELSE 1 END)::numeric / COUNT(*), 2)
          END)::text || ' %' AS valeur,
         'non nuls='||SUM(CASE WHEN value = 'null'::jsonb THEN 0 ELSE 1 END)
           ||' / total='||COUNT(*)
           ||' ; distincts='||COUNT(DISTINCT CASE WHEN value='null'::jsonb THEN NULL ELSE value END)
           AS information
  FROM (
    SELECT to_jsonb(t) - 'geom' AS js
    FROM public.ign_znieff1 AS t
  ) s,
  LATERAL jsonb_each(s.js)
  GROUP BY key
)

SELECT "Catégories et champs", valeur, information
FROM (
  SELECT * FROM vol
  UNION ALL SELECT * FROM srid_decl
  UNION ALL SELECT * FROM geom_null
  UNION ALL SELECT * FROM srid_diff
  UNION ALL SELECT * FROM invalides
  UNION ALL SELECT * FROM doublons
  UNION ALL SELECT * FROM remplissage
) u
ORDER BY ordre, "Catégories et champs";
