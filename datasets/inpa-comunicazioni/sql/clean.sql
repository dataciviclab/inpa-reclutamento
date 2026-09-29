-- Clean: tipizzazione + normalizzazione delle comunicazioni di procedura inPA
-- Input: raw_input (CSV da scripts/harvest_comunicazioni.py)
-- Output: parquet normalizzato, una riga = una comunicazione di procedura
-- Dedup: l'API può restituire record con lo stesso ID → ROW_NUMBER prende l'ultimo

WITH typed AS (
    SELECT
        normalize_string(id)                                                    AS id,
        normalize_string(concorso_id)                                           AS concorso_id,
        normalize_string(concorso_title)                                        AS concorso_title,
        normalize_string(subject)                                               AS subject,
        normalize_string(body)                                                  AS body,
        normalize_string(categoria)                                             AS categoria,
        TRY_CAST(data_pubblicazione AS DATE)                                    AS data_pubblicazione,
        normalize_string(ente)                                                  AS ente,
        ROW_NUMBER() OVER (PARTITION BY normalize_string(id)
                           ORDER BY TRY_CAST(data_pubblicazione AS DATE) DESC)  AS rn
    FROM raw_input
)
SELECT id, concorso_id, concorso_title, subject, body, categoria, data_pubblicazione, ente
FROM typed
WHERE rn = 1
