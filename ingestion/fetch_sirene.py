import requests
import os
import pandas as pd
import boto3
from io import BytesIO
from datetime import datetime
from dotenv import load_dotenv

load_dotenv("/home/ing/Bureau/finance-pipeline/.env")

# Config de l'API et AWS
INSEE_API_KEY = os.getenv("INSEE_API_KEY")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET = os.getenv("S3_BUCKET_NAME")

BASE_URL = "https://api.insee.fr/api-sirene/3.11"
HEADERS = {
    "X-INSEE-Api-Key-Integration": INSEE_API_KEY,
    "Accept": "application/json"
}

# Secteurs à ingérer (codes NAF) 
# 64 = Banques, 62 = Informatique, 47 = Commerce détail
ACTIVITES = ["64", "62", "47"]

#Chargement des données dans un fichier  json 
def fetch_entreprises(code_activite, nb=100):
    """Récupère les entreprises actives pour un secteur donné"""
    print(f"  Récupération secteur NAF {code_activite}...")
    response = requests.get(
        f"{BASE_URL}/siren",
        headers=HEADERS,
        params={
            "q": f"periode(activitePrincipaleUniteLegale:{code_activite}*) AND periode(etatAdministratifUniteLegale:A)",
            "nombre": nb,
            #"champs": "siren,denominationUniteLegale,activitePrincipaleUniteLegale,trancheEffectifsUniteLegale,dateCreationUniteLegale,categorieJuridiqueUniteLegale"
        }
    )
    if response.status_code != 200:
        print(f"  Erreur {response.status_code} : {response.text[:100]}")
        return []
    data = response.json()
    total = data.get("header", {}).get("total", 0)
    print(f"  Total disponible : {total} entreprises")
    return data.get("unitesLegales", [])




#Transaformation des données dans une dataframe

def transform_to_dataframe(entreprises):
    records = []
    for e in entreprises:
        # récupérer la période courante (index 0)
        periode = e.get("periodesUniteLegale", [{}])[0]
        records.append({
            "siren": e.get("siren"),
            "denomination": periode.get("denominationUniteLegale"),
            "activite_principale": periode.get("activitePrincipaleUniteLegale"),
            "tranche_effectifs": e.get("trancheEffectifsUniteLegale"),
            "date_creation": e.get("dateCreationUniteLegale"),
            "categorie_juridique": periode.get("categorieJuridiqueUniteLegale"),
            "date_ingestion": datetime.now().strftime("%Y-%m-%d")
        })
    return pd.DataFrame(records)

#Chargement dans S3 en format Parquet 
def upload_to_s3(df, code_activite):
    """Upload le DataFrame en Parquet vers S3 avec partitionnement par date"""
    s3 = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )
    now = datetime.now()
    s3_key = (
        f"sirene/naf={code_activite}/"
        f"year={now.year}/month={now.month:02d}/day={now.day:02d}/"
        f"entreprises.parquet"
    )
    buffer = BytesIO()
    df.to_parquet(buffer, index=False, engine="pyarrow")
    buffer.seek(0)
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=s3_key,
        Body=buffer.getvalue()
    )
    print(f"  ✓ {len(df)} entreprises uploadées → s3://{S3_BUCKET}/{s3_key}")

def main():
    print("=== Démarrage ingestion SIRENE ===")
    for code in ACTIVITES:
        print(f"\nSecteur NAF {code} :")
        entreprises = fetch_entreprises(code)
        if not entreprises:
            continue
        df = transform_to_dataframe(entreprises)
        upload_to_s3(df, code)
    print("\n=== Ingestion terminée ===")

if __name__ == "__main__":
    main()
