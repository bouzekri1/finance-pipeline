import boto3
import redshift_connector
import os
from dotenv import load_dotenv

load_dotenv()

# ── Test S3 ──────────────────────────────────────
print("Test connexion S3...")
try:
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION')
    )
    response = s3.list_buckets()
    buckets = [b['Name'] for b in response['Buckets']]
    print(f" S3 connecté — buckets disponibles : {buckets}")
except Exception as e:
    print(f" S3 erreur : {e}")

# ── Test Redshift ─────────────────────────────────
print("\nTest connexion Redshift...")
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
    print(f"  Redshift connecté")
    print(f"  Database : {row[0]}")
    print(f"  User     : {row[1]}")
    print(f"  Version  : {row[2][:50]}")
    conn.close()
except Exception as e:
    print(f" Redshift erreur : {e}")
