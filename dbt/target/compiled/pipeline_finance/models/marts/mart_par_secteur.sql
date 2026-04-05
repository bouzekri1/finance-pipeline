WITH entreprises AS (
    SELECT * FROM "dev"."finance_staging"."stg_entreprises"

)


SELECT
    activite_principale,
    COUNT(*) AS nb_entreprises,
    COUNT(CASE WHEN tranche_effectifs IS NULL THEN 1 END) AS nb_sans_effectifs
FROM entreprises
GROUP BY activite_principale