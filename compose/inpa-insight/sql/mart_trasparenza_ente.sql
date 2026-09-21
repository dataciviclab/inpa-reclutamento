-- Mart trasparenza: quanti bandi pubblicano comunicazioni vs quelli che non danno mai notizie
-- Per ente: ratio bandi con comunicazioni / totali (tra quelli con scadenza passata)
-- {support.bandi.clean} → clean parquet dei bandi
-- {support.com.clean} → clean parquet delle comunicazioni
WITH bandi_con_com AS (
    SELECT DISTINCT concorso_id
    FROM read_parquet('{support.com.clean}')
),
bandi_elegibili AS (
    SELECT
        b.ente,
        b.id,
        CASE WHEN c.concorso_id IS NOT NULL THEN 1 ELSE 0 END AS ha_comunicazioni
    FROM read_parquet('{support.bandi.clean}') b
    LEFT JOIN bandi_con_com c ON b.id = c.concorso_id
    WHERE b.is_graduatoria = FALSE
      AND b.ente IS NOT NULL
      AND b.data_scadenza < CURRENT_DATE
)
SELECT
    ente,
    COUNT(*) AS totale_bandi_chiusi,
    SUM(ha_comunicazioni) AS bandi_con_comunicazioni,
    ROUND(100.0 * SUM(ha_comunicazioni) / COUNT(*), 1) AS pct_trasparenza
FROM bandi_elegibili
GROUP BY ente
HAVING COUNT(*) >= 5
ORDER BY pct_trasparenza ASC
