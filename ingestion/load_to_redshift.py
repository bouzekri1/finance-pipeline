import redshift_connector
import os
from dotenv import load_dotenv
import boto3
import io


load_dotenv("/home/ing/Bureau/finance-pipeline/.env")

s3 = boto3.client(
    "s3",
    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name = os.getenv("AWS_REGION")
)

try:
    conn = redshift_connector.connect(
        host=os.getenv('REDSHIFT_HOST'),
        port=int(os.getenv('REDSHIFT_PORT')),
        database=os.getenv('REDSHIFT_DB'),
        user=os.getenv('REDSHIFT_USER'),
        password=os.getenv('REDSHIFT_PASSWORD')
    )
    cursor = conn.cursor()
    cursor.execute("SELECT current_database(), current_user, version()")
    row = cursor.fetchone()
    print(f"✓ Redshift connecté")
    print(f"  Database : {row[0]}")
    print(f"  User     : {row[1]}")
    print(f"  Version  : {row[2][:50]}")
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
    cursor.execute("SELECT * FROM entreprises")
    

    obj = s3.get_object(
    Bucket=os.getenv("S3_BUCKET_NAME"),
    Key="sirene/naf=64/year=2026/month=03/day=19/entreprises.parquet"
    )

    import pandas as pd
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
    conn.close()
except Exception as e:
    print(f"✗ Redshift erreur : {e}")
