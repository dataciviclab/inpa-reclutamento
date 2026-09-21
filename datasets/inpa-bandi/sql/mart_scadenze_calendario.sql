-- Mart scadenze calendario: bandi aperti raggruppati per giorno di scadenza
-- Vista calendario per chi cerca lavoro nella PA: cosa scade e quanti posti ci sono.
SELECT
    data_scadenza,
    COUNT(*) AS num_bandi,
    SUM(num_posti) AS posti_totali,
    COUNT(DISTINCT ente) AS enti_diversi,
    STRING_AGG(DISTINCT categoria, ', ' ORDER BY categoria) AS categorie
FROM clean_input
WHERE status = 'OPEN'
  AND data_scadenza IS NOT NULL
  AND data_scadenza >= CURRENT_DATE
GROUP BY data_scadenza
ORDER BY data_scadenza
