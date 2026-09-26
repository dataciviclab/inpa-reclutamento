-- Mart trasparenza: % bandi con comunicazioni per ente
SELECT
    ente,
    COUNT(*) AS totale_bandi_chiusi,
    SUM(ha_comunicazioni) AS bandi_con_comunicazioni,
    ROUND(100.0 * SUM(ha_comunicazioni) / COUNT(*), 1) AS pct_trasparenza
FROM clean_input
WHERE NOT is_graduatoria
  AND ente IS NOT NULL
  AND data_scadenza < CURRENT_DATE
GROUP BY ente
HAVING COUNT(*) >= 5
ORDER BY pct_trasparenza ASC
