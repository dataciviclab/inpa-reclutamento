#!/usr/bin/env python3
"""Health check per l'API inPA — verifica che la fonte sia raggiungibile e strutturalmente valida.

Eseguita prima di ogni harvest per fallire early se l'API cambia.

Uso:
    python3 scripts/source_health_check.py
    python3 scripts/source_health_check.py --verbose
"""

from __future__ import annotations

import argparse
import sys

import requests

API_BASE = "https://portale.inpa.gov.it/concorsi-smart/api"
SEARCH_ENDPOINT = API_BASE + "/concorso-public-area/search-better"
COMMS_ENDPOINT = API_BASE + "/communication/user/public-area/search"

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (DataCivicLab dataset-incubator)",
    "Accept": "application/json",
}

# Campi obbligatori nella risposta search bandi
REQUIRED_BANDI_FIELDS = {
    "id",
    "codice",
    "titolo",
    "dataPubblicazione",
    "dataScadenza",
    "calculatedStatus",
    "tipoProcedura",
    "numPosti",
}

# Campi obbligatori nella risposta search comunicazioni
REQUIRED_COMMS_FIELDS = {
    "id",
    "concorsoId",
    "concorsoTitle",
    "subject",
    "categoryName",
    "dateFirstPublish",
    "companyName",
}


def check_bandi(session: requests.Session, verbose: bool) -> bool:
    """Verifica endpoint bandi: raggiungibilità + struttura risposta."""
    body = {
        "text": "",
        "categoriaId": None,
        "regioneId": None,
        "status": ["OPEN"],
        "settoreId": None,
        "provinciaCodice": None,
        "dateFrom": None,
        "dateTo": None,
        "livelliAnzianitaIds": None,
        "tipoImpiegoId": None,
        "salaryMin": None,
        "salaryMax": None,
        "enteRiferimentoName": "",
    }
    try:
        resp = session.post(SEARCH_ENDPOINT, params={"page": 0, "size": 1}, json=body, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"FAIL bandi: {e}", file=sys.stderr)
        return False

    data = resp.json()
    if verbose:
        print(
            f"OK bandi: status={resp.status_code}, totalElements={data.get('totalElements', '?')}"
        )

    # Verifica struttura
    if "content" not in data:
        print("FAIL bandi: campo 'content' mancante nella risposta", file=sys.stderr)
        return False

    content = data.get("content", [])
    if content:
        first = content[0]
        missing = REQUIRED_BANDI_FIELDS - set(first.keys())
        if missing:
            print(f"FAIL bandi: campi mancanti nel record: {missing}", file=sys.stderr)
            return False
        if verbose:
            print(f"OK bandi: struttura record valida ({len(first)} campi)")

    return True


def check_comunicazioni(session: requests.Session, verbose: bool) -> bool:
    """Verifica endpoint comunicazioni: raggiungibilità + struttura risposta."""
    body = {
        "subject": "",
        "concorsoId": None,
        "categoryId": None,
        "publishDateFrom": None,
        "publishDateTo": None,
        "effectiveDateFrom": None,
        "effectiveDateTo": None,
        "companyName": "",
    }
    try:
        resp = session.post(COMMS_ENDPOINT, params={"page": 0, "size": 1}, json=body, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"FAIL comunicazioni: {e}", file=sys.stderr)
        return False

    data = resp.json()
    if verbose:
        print(
            f"OK comunicazioni: status={resp.status_code}, totalElements={data.get('totalElements', '?')}"
        )

    if "content" not in data:
        print("FAIL comunicazioni: campo 'content' mancante nella risposta", file=sys.stderr)
        return False

    content = data.get("content", [])
    if content:
        first = content[0]
        missing = REQUIRED_COMMS_FIELDS - set(first.keys())
        if missing:
            print(f"FAIL comunicazioni: campi mancanti nel record: {missing}", file=sys.stderr)
            return False
        if verbose:
            print(f"OK comunicazioni: struttura record valida ({len(first)} campi)")

    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verbose", action="store_true", help="mostra dettagli")
    args = parser.parse_args()

    session = requests.Session()
    session.headers.update(DEFAULT_HEADERS)

    ok_bandi = check_bandi(session, args.verbose)
    ok_comms = check_comunicazioni(session, args.verbose)

    if ok_bandi and ok_comms:
        print("OK: tutti gli endpoint sono raggiungibili e validi", file=sys.stderr)
        return 0
    else:
        print("FAIL: almeno un endpoint non disponibile o cambiato", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
