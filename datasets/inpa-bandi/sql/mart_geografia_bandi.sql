-- Mart geografia: bandi per regione (senza multi-sede)
-- Risponde a: dove si cerca più personale?
SELECT
    regione,
    COUNT(*) AS n_bandi,
    SUM(num_posti) AS posti_totali,
    COUNT(DISTINCT ente) AS enti_diversi,
    ROUND(AVG(num_posti), 1) AS media_posti_per_bando
FROM clean_input
WHERE status = 'OPEN'
  AND NOT is_graduatoria
  AND regione IS NOT NULL
  AND regione NOT LIKE '%|%'
GROUP BY 1
ORDER BY 2 DESC
