-- Mart tipo procedura: breakdown bandi per tipo di procedura
-- Risponde a: come assume la PA? Esami, colloqui, titoli?
SELECT
    tipo_procedura,
    COUNT(*) AS n_bandi,
    SUM(num_posti) AS posti_totali,
    COUNT(DISTINCT ente) AS enti_diversi,
    ROUND(AVG(num_posti), 1) AS media_posti_per_bando
FROM clean_input
WHERE status = 'OPEN'
  AND NOT is_graduatoria
  AND tipo_procedura IS NOT NULL
GROUP BY 1
ORDER BY 2 DESC
