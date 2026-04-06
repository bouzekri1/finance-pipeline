

  create view "dev"."finance_staging"."stg_entreprises__dbt_tmp" as (
    WITH source AS (
    SELECT * FROM "dev"."public"."entreprises"
),

cleaned AS (
    SELECT
        siren,
        denomination,
        activite_principale,
        NULLIF(tranche_effectifs, 'NN') AS tranche_effectifs,
        CAST(date_creation AS DATE)     AS date_creation,
        categorie_juridique,
        CAST(date_ingestion AS DATE)    AS date_ingestion
        FROM source
        WHERE siren IS NOT NULL 
)

SELECT * FROM cleaned
  ) ;
