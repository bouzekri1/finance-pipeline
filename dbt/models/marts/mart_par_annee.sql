WITH entreprises AS (
    SELECT * FROM {{ ref('stg_entreprises') }}

)

SELECT
    EXTRACT(YEAR FROM date_creation) AS annee_de_creation,
    COUNT(*) AS nb_entreprises
FROM entreprises
GROUP BY annee_de_creation
ORDER BY annee_de_creation ASC
