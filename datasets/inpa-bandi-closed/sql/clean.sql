-- Clean: tipizzazione + normalizzazione del CSV flat prodotto da harvest_bandi.py
-- Input: raw_input (CSV da scripts/harvest_bandi.py --status CLOSED)
-- Output: parquet normalizzato, una riga = un bando inPA (archivio storico)

WITH typed AS (
    SELECT
        normalize_string(id)                                                    AS id,
        normalize_string(codice)                                                AS codice,
        normalize_string(titolo)                                                AS titolo,
        normalize_string(figura_ricercata)                                      AS figura_ricercata,
        TRY_CAST(normalize_string(descrizione) AS VARCHAR)                      AS descrizione,
        CASE WHEN EXTRACT(YEAR FROM TRY_CAST(data_pubblicazione AS DATE)) >= 2000
             THEN TRY_CAST(data_pubblicazione AS DATE) END                      AS data_pubblicazione,
        CASE WHEN EXTRACT(YEAR FROM TRY_CAST(data_scadenza AS DATE)) >= 2000
             THEN TRY_CAST(data_scadenza AS DATE) END                           AS data_scadenza,
        CASE WHEN EXTRACT(YEAR FROM TRY_CAST(data_visibilita AS DATE)) >= 2000
             THEN TRY_CAST(data_visibilita AS DATE) END                         AS data_visibilita,
        normalize_string(tipo_procedura)                                        AS tipo_procedura,
        CASE WHEN cast_int(num_posti) IS NOT NULL
                  AND NOT (regexp_matches(cast_int(num_posti)::VARCHAR, '^9+$') AND cast_int(num_posti) > 99)
                  AND NOT cast_int(num_posti) > 50000
             THEN cast_int(num_posti) END                                    AS num_posti,
        CASE WHEN cast_int(num_posti) IS NOT NULL
                  AND cast_int(num_posti) > 50000
             THEN TRUE ELSE FALSE END                                        AS is_graduatoria,
        normalize_string(status)                                                AS status,
        normalize_string(status_label)                                          AS status_label,
        normalize_string(categoria)                                             AS categoria,
        normalize_string(settore)                                               AS settore,
        normalize_string(regione)                                               AS regione,
        normalize_string(provincia)                                             AS provincia,
        normalize_string(ente)                                                  AS ente,
        normalize_string(enti_riferimento)                                      AS enti_riferimento,
        normalize_string(categorie)                                             AS categorie,
        normalize_string(settori)                                               AS settori,
        normalize_string(sedi)                                                  AS sedi,
        cast_double(salary_min)                                                 AS salary_min,
        cast_double(salary_max)                                                 AS salary_max,
        normalize_string(link_inpa)                                             AS link_inpa
    FROM raw_input
)
SELECT
    id, codice, titolo, figura_ricercata, descrizione,
    data_pubblicazione, data_scadenza, data_visibilita, tipo_procedura, num_posti,
    is_graduatoria,
    status, status_label, categoria, settore, regione, provincia, ente,
    enti_riferimento, categorie, settori, sedi,
    salary_min, salary_max, link_inpa
FROM typed
