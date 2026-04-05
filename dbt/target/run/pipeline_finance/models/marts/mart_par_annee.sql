
  
    

  create  table
    "dev"."finance_marts"."mart_par_annee__dbt_tmp"
    
    
    
  as (
    WITH entreprises AS (
    SELECT * FROM "dev"."finance_staging"."stg_entreprises"

)

SELECT
    EXTRACT(YEAR FROM date_creation) AS annee_de_creation,
    COUNT(*) AS nb_entreprises
FROM entreprises
GROUP BY annee_de_creation
  );
  