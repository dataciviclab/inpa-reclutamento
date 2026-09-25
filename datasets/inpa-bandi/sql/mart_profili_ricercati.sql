-- Mart profili ricercati: normalizzazione delle figure professionali richieste
-- Risponde a: che tipo di personale cerca la PA?
-- Normalizzazione: case-insensitive, unifica varianti dello stesso profilo
SELECT
    CASE
        WHEN UPPER(figura_ricercata) LIKE '%ISTRUTTORE%AMMINISTRAT%' THEN 'Istruttore Amministrativo'
        WHEN UPPER(figura_ricercata) LIKE '%ISTRUTTORE%CONTAB%' THEN 'Istruttore Amministrativo'
        WHEN UPPER(figura_ricercata) LIKE '%ISTRUTTORE%TECN%' THEN 'Istruttore Tecnico'
        WHEN UPPER(figura_ricercata) LIKE '%ISTRUTTORE%' THEN 'Istruttore'
        WHEN UPPER(figura_ricercata) LIKE '%FUNZIONARI%TECN%' OR UPPER(figura_ricercata) LIKE '%FUNZIONARIO%TECN%' THEN 'Funzionario Tecnico'
        WHEN UPPER(figura_ricercata) LIKE '%FUNZIONARI%AMMINISTR%' OR UPPER(figura_ricercata) LIKE '%FUNZIONARIO%AMMINISTR%' THEN 'Funzionario Amministrativo'
        WHEN UPPER(figura_ricercata) LIKE '%FUNZIONARI%CONTAB%' OR UPPER(figura_ricercata) LIKE '%FUNZIONARIO%CONTAB%' THEN 'Funzionario Amministrativo'
        WHEN UPPER(figura_ricercata) LIKE '%FUNZIONARI%VIGILANZA%' OR UPPER(figura_ricercata) LIKE '%FUNZIONARIO%VIGILANZA%' THEN 'Funzionario di Vigilanza'
        WHEN UPPER(figura_ricercata) LIKE '%FUNZIONARI%' OR UPPER(figura_ricercata) LIKE '%FUNZIONARIO%' THEN 'Funzionario'
        WHEN UPPER(figura_ricercata) LIKE '%DOCENTE%CONTRATT%' THEN 'Docente a contratto'
        WHEN UPPER(figura_ricercata) LIKE '%DOCENTE%PRIMA%FASCIA%' OR UPPER(figura_ricercata) LIKE '%DOCENTE%SECONDA%FASCIA%' THEN 'Docente AFAM'
        WHEN UPPER(figura_ricercata) LIKE '%DOCENTI%' OR UPPER(figura_ricercata) LIKE '%DOCENTE%' THEN 'Docente'
        WHEN UPPER(figura_ricercata) LIKE '%INFERMIER%' THEN 'Infermiere'
        WHEN UPPER(figura_ricercata) LIKE '%POLIZIA%' THEN 'Polizia Locale'
        WHEN UPPER(figura_ricercata) LIKE '%ASSISTENTE%SOCIALE%' THEN 'Assistente Sociale'
        WHEN UPPER(figura_ricercata) LIKE '%OPERATORE%SOCIO%S%' THEN 'OSS'
        WHEN UPPER(figura_ricercata) LIKE '%OPERATORE%ESPERTO%' THEN 'Operatore Esperto'
        WHEN UPPER(figura_ricercata) LIKE '%OPERATORE%' THEN 'Operatore'
        WHEN UPPER(figura_ricercata) LIKE '%DIRIGENTE%MEDICO%' THEN 'Dirigente Medico'
        WHEN UPPER(figura_ricercata) LIKE '%DIRIGENTE%' THEN 'Dirigente'
        WHEN UPPER(figura_ricercata) LIKE '%FISIOTERAPISTA%' THEN 'Fisioterapista'
        WHEN UPPER(figura_ricercata) LIKE '%COLLABORATORE%' THEN 'Collaboratore'
        WHEN UPPER(figura_ricercata) LIKE '%INGEGNERE%' THEN 'Ingegnere'
        WHEN UPPER(figura_ricercata) LIKE '%AVVOCAT%' THEN 'Avvocato'
        WHEN UPPER(figura_ricercata) LIKE '%GEOMETRA%' THEN 'Geometra'
        WHEN UPPER(figura_ricercata) LIKE '%AGGIORNAMENTO%' OR UPPER(figura_ricercata) LIKE '%GRADUATORIA%' THEN 'Graduatoria/Aggiornamento'
        ELSE 'Altro'
    END AS profilo,
    COUNT(*) AS n_bandi,
    SUM(num_posti) AS posti_totali,
    COUNT(DISTINCT ente) AS enti_diversi
FROM clean_input
WHERE status = 'OPEN' AND NOT is_graduatoria
GROUP BY 1
ORDER BY 2 DESC
