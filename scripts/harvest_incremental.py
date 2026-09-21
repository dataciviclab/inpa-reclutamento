#!/usr/bin/env python3
"""Harvest incrementale giornaliero da inPA.

Scarica solo:
- Bandi OPEN (senza dettaglio, ~2 min)
- Comunicazioni delle ultime 7gg (~30 sec)

Output: CSV flat da passare a toolkit run raw|clean|mart.
Usage:
    python scripts/harvest_incremental.py
"""

from __future__ import annotations

import csv
import html
import re
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import requests

API_BASE = "https://portale.inpa.gov.it/concorsi-smart/api"
BANDI_ENDPOINT = API_BASE + "/concorso-public-area/search-better"
COM_ENDPOINT = API_BASE + "/communication/user/public-area/search"

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (DataCivicLab inpa-reclutamento)",
    "Accept": "application/json",
}

TAG_RE = re.compile(r"<[^>]+>")
REGIONI = {
    "Abruzzo", "Basilicata", "Calabria", "Campania", "Emilia-Romagna",
    "Emilia Romagna", "Friuli-Venezia Giulia", "Lazio", "Liguria",
    "Lombardia", "Marche", "Molise", "Piemonte", "Puglia", "Sardegna",
    "Sicilia", "Toscana", "Trentino-Alto Adige", "Umbria", "Valle d'Aosta",
    "Veneto",
}


def _clean_html(raw: str | None) -> str | None:
    if raw is None:
        return None
    text = TAG_RE.sub("", raw)
    text = html.unescape(text).strip()
    return text or None


def _join(values: list | None, sep: str = "|") -> str | None:
    if not values:
        return None
    cleaned = [str(v).strip() for v in values if str(v).strip()]
    return sep.join(cleaned) if cleaned else None


def _first(values: list | None) -> str | None:
    joined = _join(values)
    return joined.split("|")[0] if joined else None


def _names(values: list | None) -> list[str]:
    if not values:
        return []
    out = []
    for v in values:
        if isinstance(v, dict):
            name = (v.get("name") or "").strip()
            if name:
                out.append(name)
        elif isinstance(v, str) and v.strip():
            out.append(v.strip())
    return sorted(set(out))


def _regioni(sedi: list | None) -> str | None:
    if not sedi:
        return None
    regs = set()
    for s in sedi:
        if isinstance(s, dict) and s.get("regioneDenominazione"):
            regs.add(s["regioneDenominazione"].strip())
        elif isinstance(s, str) and s.strip() in REGIONI:
            regs.add(s.strip())
    return _join(sorted(regs))


def _province(sedi: list | None) -> str | None:
    if not sedi:
        return None
    provs = set()
    for s in sedi:
        if isinstance(s, dict) and s.get("provinciaDenominazione"):
            provs.add(s["provinciaDenominazione"].strip())
        elif isinstance(s, str) and s.strip() and s.strip() not in REGIONI:
            provs.add(s.strip())
    return _join(sorted(provs))


def _flatten_bando(item: dict) -> dict:
    return {
        "id": item.get("id"),
        "codice": item.get("codice"),
        "titolo": item.get("titolo"),
        "descrizione": _clean_html(item.get("descrizioneBreve") or item.get("descrizione")),
        "figura_ricercata": item.get("figuraRicercata"),
        "data_pubblicazione": item.get("dataPubblicazione"),
        "data_scadenza": item.get("dataScadenza"),
        "data_visibilita": item.get("dataVisibilita"),
        "tipo_procedura": item.get("tipoProcedura"),
        "num_posti": item.get("numPosti"),
        "status": item.get("calculatedStatus"),
        "status_label": item.get("statusLabel"),
        "categoria": _first(item.get("categorie")),
        "settore": _join(_names(item.get("settori"))),
        "regione": _regioni(item.get("sedi")),
        "provincia": _province(item.get("sedi")),
        "ente": _first(item.get("entiRiferimento")),
        "enti_riferimento": _join(item.get("entiRiferimento")),
        "settori": _join(_names(item.get("settori")), sep="|"),
        "categorie": _join(_names(item.get("categorie")), sep="|"),
        "sedi": _join(
            [
                f"{s.get('regioneDenominazione')}-{s.get('provinciaDenominazione')}"
                if isinstance(s, dict) and s.get("provinciaDenominazione")
                else s
                for s in (item.get("sedi") or [])
            ],
            sep="|",
        ),
        "company_district_code": None,
        "link_sito_pa": None,
        "email_referente": None,
        "richiede_pagamento": None,
        "pec_obbligatoria": None,
        "is_remote": None,
        "salary_min": None,
        "salary_max": None,
        "link_gazzetta_ufficiale": None,
        "n_allegati": None,
    }


def _flatten_comunicazione(item: dict) -> dict:
    return {
        "id": item.get("id"),
        "concorso_id": item.get("concorsoId"),
        "concorso_title": item.get("concorsoTitle"),
        "subject": item.get("subject"),
        "body": _clean_html(item.get("body")),
        "categoria": item.get("categoryName"),
        "data_pubblicazione": item.get("dateFirstPublish"),
        "ente": item.get("companyName"),
    }


def harvest_bandi(session: requests.Session, date_from: str) -> list[dict]:
    """Harvest bandi OPEN pubblicati/aggiornati da date_from."""
    body = {
        "text": "",
        "categoriaId": None,
        "regioneId": None,
        "status": ["OPEN"],
        "settoreId": None,
        "provinciaCodice": None,
        "dateFrom": date_from,
        "dateTo": None,
        "livelliAnzianitaIds": None,
        "tipoImpiegoId": None,
        "salaryMin": None,
        "salaryMax": None,
        "enteRiferimentoName": "",
    }

    first_resp = session.post(
        BANDI_ENDPOINT, params={"page": 0, "size": 500}, json=body, timeout=60
    )
    first_resp.raise_for_status()
    data = first_resp.json()
    total_pages = data.get("totalPages", 1)
    print(f"inPA bandi incremental: {data.get('totalElements', 0)} elementi, {total_pages} pagine", file=sys.stderr)

    rows = [_flatten_bando(item) for item in data.get("content", [])]
    for page in range(1, total_pages):
        time.sleep(0.3)
        resp = session.post(
            BANDI_ENDPOINT, params={"page": page, "size": 500}, json=body, timeout=60
        )
        resp.raise_for_status()
        rows.extend(_flatten_bando(item) for item in resp.json().get("content", []))

    print(f"inPA bandi incremental: {len(rows)} bandi raccolti", file=sys.stderr)
    return rows


def harvest_comunicazioni(session: requests.Session, date_from: str) -> list[dict]:
    """Harvest comunicazioni pubblicate da date_from."""
    body = {
        "subject": "",
        "concorsoId": None,
        "categoryId": None,
        "publishDateFrom": date_from,
        "publishDateTo": None,
        "effectiveDateFrom": None,
        "effectiveDateTo": None,
        "companyName": "",
    }

    first_resp = session.post(
        COM_ENDPOINT, params={"page": 0, "size": 100}, json=body, timeout=60
    )
    first_resp.raise_for_status()
    data = first_resp.json()
    total_pages = data.get("totalPages", 1)
    print(f"inPA comunicazioni incremental: {data.get('totalElements', 0)} elementi", file=sys.stderr)

    rows = [_flatten_comunicazione(item) for item in data.get("content", [])]
    for page in range(1, total_pages):
        time.sleep(0.2)
        resp = session.post(
            COM_ENDPOINT, params={"page": page, "size": 100}, json=body, timeout=60
        )
        resp.raise_for_status()
        rows.extend(_flatten_comunicazione(item) for item in resp.json().get("content", []))

    print(f"inPA comunicazioni incremental: {len(rows)} comunicazioni", file=sys.stderr)
    return rows


def write_csv(rows: list[dict], path: Path) -> None:
    if not rows:
        print(f"WARNING:nessun dato da scrivere in {path}", file=sys.stderr)
        return
    fieldnames = sorted({k for r in rows for k in r})
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(f"Scritto {path} ({len(rows)} righe)", file=sys.stderr)


def main() -> int:
    date_from = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    print(f"Harvest incrementale da {date_from}", file=sys.stderr)

    session = requests.Session()
    session.headers.update(DEFAULT_HEADERS)

    out_dir = Path("data/raw")
    out_dir.mkdir(parents=True, exist_ok=True)

    # Bandi OPEN (ultimi 7gg, senza dettaglio)
    bandi = harvest_bandi(session, date_from)
    write_csv(bandi, out_dir / "bandi_daily.csv")

    # Comunicazioni (ultimi 7gg)
    com = harvest_comunicazioni(session, date_from)
    write_csv(com, out_dir / "comunicazioni_daily.csv")

    return 0


if __name__ == "__main__":
    sys.exit(main())
