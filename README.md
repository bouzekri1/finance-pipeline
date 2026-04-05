# finance-pipeline

Pipeline de données end-to-end ingérant les données d'entreprises françaises 
(API SIRENE INSEE) vers un entrepôt de données cloud, avec orchestration 
automatisée et transformation via dbt.

## Architecture
```
INSEE SIRENE API
      ↓
fetch_sirene.py (Python)
      ↓
Amazon S3 (Parquet, partitionné par NAF/date)
      ↓
load_many_to_redshift.py (Python)
      ↓
Amazon Redshift Serverless
      ↓
dbt (staging → marts)
      ↓
finance_staging.stg_entreprises (vue)
finance_marts.mart_par_secteur  (table)
finance_marts.mart_par_annee    (table)

Orchestration : Apache Airflow 2.8.1
```

## Stack technique

| Couche | Technologie |
|---|---|
| Ingestion | Python, requests, pandas, pyarrow |
| Stockage brut | Amazon S3 (format Parquet, partitionnement Hive) |
| Entrepôt | Amazon Redshift Serverless |
| Transformation | dbt 1.8.1 + dbt-redshift |
| Orchestration | Apache Airflow 2.8.1 (Docker) |
| Infrastructure | AWS IAM, S3, Redshift Serverless |
| Versioning | Git / GitHub |

## Structure du projet
```
finance-pipeline/
├── airflow/
│   ├── dags/
│   │   └── finance_pipeline_dag.py   # DAG Airflow
│   ├── Dockerfile                     # Image custom avec dbt
│   └── docker-compose.yml             # 4 conteneurs Airflow
├── dbt/
│   └── models/
│       ├── staging/
│       │   ├── sources.yml            # Déclaration source SIRENE
│       │   └── stg_entreprises.sql    # Nettoyage données brutes
│       └── marts/
│           ├── mart_par_secteur.sql   # Agrégation par secteur NAF
│           └── mart_par_annee.sql     # Évolution par année
├── ingestion/
│   ├── fetch_sirene.py                # API INSEE → S3
│   └── load_many_to_redshift.py       # S3 → Redshift
├── .env.example                       # Template variables d'environnement
├── .gitignore
└── README.md
```

## Données

Source : [API SIRENE INSEE](https://portail-api.insee.fr) — base officielle 
des entreprises françaises (10M+ établissements).

Secteurs ingérés :

| Code NAF | Secteur | Entreprises disponibles |
|---|---|---|
| 64 | Activités financières et bancaires | ~342 000 |
| 62 | Informatique et services numériques | ~520 000 |
| 47 | Commerce de détail | ~2 400 000 |

## Modèles dbt

### staging — `stg_entreprises`
Vue de nettoyage des données brutes :
- Cast des dates (`VARCHAR` → `DATE`)
- Remplacement de `NN` par `NULL` dans `tranche_effectifs`
- Filtre sur `siren IS NOT NULL`

### marts — `mart_par_secteur`
Table d'agrégation par secteur NAF :
- Nombre d'entreprises par secteur
- Nombre d'entreprises sans effectifs renseignés

### marts — `mart_par_annee`
Table d'évolution des créations d'entreprises :
- Nombre de créations par année
- Trié par année croissante

## Pipeline Airflow

Le DAG `finance_pipeline` orchestre 3 tâches quotidiennes :
```
fetch_sirene → load_to_redshift → dbt_run
```

- `fetch_sirene` : appel API INSEE → sauvegarde Parquet dans S3
- `load_to_redshift` : lecture S3 → insertion dans Redshift
- `dbt_run` : exécution des modèles staging et marts

## Installation

### Prérequis
- Docker + Docker Compose
- Python 3.8+
- Compte AWS (S3 + Redshift Serverless)
- Clé API INSEE SIRENE

### 1. Cloner le projet
```bash
git clone https://github.com/bouzekri1/finance-pipeline.git
cd finance-pipeline
```

### 2. Configurer les variables d'environnement
```bash
cp .env.example .env
nano .env
```

Remplir les valeurs :
```
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=eu-north-1
S3_BUCKET_NAME=finance-pipeline-raw
REDSHIFT_HOST=
REDSHIFT_PORT=5439
REDSHIFT_DB=dev
REDSHIFT_USER=admin
REDSHIFT_PASSWORD=
INSEE_API_KEY=
AIRFLOW_UID=998
AIRFLOW_GID=0
```

### 3. Configurer dbt
```bash
mkdir -p ~/.dbt
nano ~/.dbt/profiles.yml
```
```yaml
pipeline_finance:
  target: dev
  outputs:
    dev:
      type: redshift
      host: <REDSHIFT_HOST>
      port: 5439
      dbname: dev
      schema: finance
      user: admin
      password: <REDSHIFT_PASSWORD>
      threads: 1
      method: database
```

### 4. Lancer Airflow
```bash
cd airflow
docker compose up airflow-init
docker compose up -d
```

Interface disponible sur `http://localhost:8080` (admin/admin).

### 5. Tester les connexions
```bash
python3 -m venv venv
source venv/bin/activate
pip install boto3 redshift-connector python-dotenv pandas pyarrow

python ingestion/test_connections.py
```

### 6. Lancer le pipeline manuellement
```bash
# Ingestion API → S3
python ingestion/fetch_sirene.py

# Chargement S3 → Redshift
python ingestion/load_many_to_redshift.py

# Transformation dbt
cd dbt && dbt run
```

Ou via l'interface Airflow en déclenchant le DAG `finance_pipeline`.

## Bonnes pratiques appliquées

- Credentials dans `.env`, jamais dans le code
- Utilisateur système dédié `airflow` avec permissions minimales
- Format Parquet avec partitionnement Hive pour l'optimisation des requêtes
- Séparation des couches : raw (S3) → staging (vues) → marts (tables)
- Tests de connexion avant chaque déploiement
- Principe du moindre privilège sur IAM

## Auteur

Abdessamad Bouzekri — [github.com/bouzekri1](https://github.com/bouzekri1)
