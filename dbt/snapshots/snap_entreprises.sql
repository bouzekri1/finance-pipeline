{% snapshot snap_entreprises %}

{{
    config(
        target_schema='snapshots',
        unique_key='siren',
        strategy='check',
        check_cols=['activite_principale', 'categorie_juridique', 'tranche_effectifs']
    )
}}

SELECT * FROM {{ source('sirene', 'entreprises') }}

{% endsnapshot %}
