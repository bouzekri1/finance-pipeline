import redshift_connector
import os
from dotenv import load_dotenv
import boto3
import io
import pandas as pd
from datetime import datetime



load_dotenv("/home/ing/Bureau/finance-pipeline/.env")

# Secteurs à ingérer (codes NAF) 
secteurs = [
    "naf=64",
    "naf=62", 
    "naf=47"
]

#Définition de notre S3
s3 = boto3.client(
    "s3",
    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name = os.getenv("AWS_REGION")
)

def main():
    #Connexion to Redshift
    try:
        conn = redshift_connector.connect(
            host=os.getenv('REDSHIFT_HOST'),
            port=int(os.getenv('REDSHIFT_PORT')),
            database=os.getenv('REDSHIFT_DB'),
            user=os.getenv('REDSHIFT_USER'),
            password=os.getenv('REDSHIFT_PASSWORD')
        )
        cursor = conn.cursor()
        #Affichage des information de la bdd et état de la connexion
        cursor.execute("SELECT current_database(), current_user, version()")
        row = cursor.fetchone()
        print(f"  Redshift connecté")
        print(f"  Database : {row[0]}")
        print(f"  User     : {row[1]}")
        print(f"  Version  : {row[2][:50]}")
        cursor.execute("TRUNCATE TABLE entreprises")
        #Création de la table entreprises
        cursor.execute("CREATE TABLE IF NOT EXISTS  entreprises (" \
        "siren VARCHAR(9)," \
        "denomination VARCHAR(500)," \
        "activite_principale VARCHAR(10)," \
        "tranche_effectifs VARCHAR(2)," \
        "date_creation VARCHAR(10)," \
        "categorie_juridique VARCHAR(4)," \
        "date_ingestion VARCHAR(10)" \
        ")")
        conn.commit()
        
        #Extraction des données de S3 et chargement des données dans Redshift
        now = datetime.now()
        for secteur in secteurs:
            
            obj = s3.get_object(
            Bucket=os.getenv("S3_BUCKET_NAME"),
            #clé du fichier parquet
            Key=f"sirene/{secteur}/year={now.year}/month={now.month:02d}/day={now.day:02d}/entreprises.parquet"
            )
        #Appel au script read_parquet
            df = pd.read_parquet(io.BytesIO(obj["Body"].read()))

            for _, row in df.iterrows():
                cursor.execute("""
                    INSERT INTO entreprises VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    row["siren"],
                    row["denomination"],
                    row["activite_principale"],
                    row["tranche_effectifs"],
                    row["date_creation"],
                    row["categorie_juridique"],
                    row["date_ingestion"]
                ))

                conn.commit()
                print(f"++{len(df)} lignes insérées pour {secteur}")
        conn.close()
        print("=== FIn du chargement ===")
    except Exception as e:
        print(f" Redshift erreur : {e}")

if __name__ == "__main__":
    main()
