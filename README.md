<img width="796" height="552" alt="Architecture" src="https://github.com/user-attachments/assets/0e93bc3f-49fe-42f2-b4a2-d815fe0db55d" />

# finance-pipeline

Pipeline de données qui récupère les entreprises françaises depuis l'API 
SIRENE de l'INSEE, les stocke dans S3 et les transforme dans Redshift 
avec dbt. Le tout orchestré par Airflow.

Projet perso pour pratiquer la stack Data Engineer moderne :
Airflow · dbt · S3 · Redshift · Python

## Ce que ça fait

Tous les jours, le pipeline :
1. Appelle l'API SIRENE pour récupérer 100 entreprises par secteur (banque, 
   informatique, commerce)
2. Sauvegarde les données brutes en Parquet dans S3
3. Les charge dans Redshift
4. Lance dbt pour nettoyer et agréger les données

## Stack

- **Ingestion** : Python + requests + pandas
- **Stockage** : S3 (Parquet, partitionné par date)
- **Entrepôt** : Redshift Serverless
- **Transformation** : dbt
- **Orchestration** : Airflow (Docker)
- **Cloud** : AWS (IAM, S3, Redshift)

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
    └── load_to_redshift.py            # S3 → Redshift
    └── read_parquet.py               # Lecture du contenu d'un fichier parquet
    └── snip_redshift_ingested.py      # Contenu d'une table ajoutée dans Redshift     
├── .env.example                       # Template variables d'environnement
├── .gitignore
└── README.md
```
## Lancer le projet

### Prérequis

- Docker
- Python 3.8+
- Compte AWS avec S3 + Redshift Serverless
- Clé API INSEE (gratuit sur portail-api.insee.fr)

### Setup
```bash
git clone https://github.com/bouzekri1/finance-pipeline.git
cd finance-pipeline
cp .env.example .env
# remplir .env avec tes credentials
```

Configurer dbt dans `~/.dbt/profiles.yml` :
```yaml
pipeline_finance:
  target: dev
  outputs:
    dev:
      type: redshift
      host: 
      port: 5439
      dbname: dev
      schema: finance
      user: admin
      password: 
      threads: 1
      method: database
```

Lancer Airflow :
```bash
cd airflow
docker compose up airflow-init
docker compose up -d
# interface sur http://localhost:8080 (admin/admin)
```

### Tester les connexions
```bash
pip install -r requirements.txt
python ingestion/test_connections.py
```

### Lancer manuellement
```bash
python ingestion/fetch_sirene.py
python ingestion/load_many_to_redshift.py
cd dbt && dbt run
```

Ou déclencher le DAG `finance_pipeline` dans Airflow.

## Données

Source : API SIRENE INSEE — 3 secteurs ingérés :

| NAF | Secteur |
|---|---|
| 64 | Finance et banque |
| 62 | Informatique |
| 47 | Commerce de détail |

## Notes

- Les credentials ne sont jamais dans le code, uniquement dans `.env`
- Le format Parquet est partitionné par `naf/year/month/day` pour 
  optimiser les requêtes Redshift
- dbt sépare les données en deux couches : staging (nettoyage) 
  et marts (agrégations)
