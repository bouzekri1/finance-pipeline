# COnsulter les donnée insérées dans Redshift

import redshift_connector
import os
from dotenv import load_dotenv


load_dotenv("/home/ing/Bureau/finance-pipeline/.env")

try:
    conn = redshift_connector.connect(
        host=os.getenv('REDSHIFT_HOST'),
        port=int(os.getenv('REDSHIFT_PORT')),
        database=os.getenv('REDSHIFT_DB'),
        user=os.getenv('REDSHIFT_USER'),
        password=os.getenv('REDSHIFT_PASSWORD')
    )
    cursor = conn.cursor()
    # cursor.execute("SELECT COUNT(*) FROM entreprises")
    # count = cursor.fetchone()
    # print(f"Nombre de ligne: {count[0]}")

    cursor.execute("SELECT * FROM finance_marts.mart_par_annee")
    rows=cursor.fetchall()
    for row in rows:
        print(row)
    conn.close()
except Exception as e:
    print(f" Redshift erreur : {e}")

