#!/usr/bin/env python3
"""Harvest bandi dal Portale inPA (Portale del Reclutamento PA).

Chiama l'API pubblica non documentata ``concorsi-smart`` di inPA e produce un
CSV flat dei bandi.

Uso:
    python3 harvest_bandi.py <output.csv> --status OPEN     # ~20s
    python3 harvest_bandi.py <output.csv> --status CLOSED   # ~12min
    python3 harvest_bandi.py <output.csv>                   # default OPEN

Il link diretto al bando su inPA viene calcolato dall'ID:
https://www.inpa.gov.it/bandi-e-avvisi/dettaglio-bando-avviso/?concorso_id={id}
"""

from __future__ import annotations

import argparse
import csv
import html
import re
import sys
import time
from pathlib import Path

import requests

API_BASE = "https://portale.inpa.gov.it/concorsi-smart/api"
SEARCH_ENDPOINT = API_BASE + "/concorso-public-area/search-better"
INPA_LINK_TEMPLATE = (
    "https://www.inpa.gov.it/bandi-e-avvisi/dettaglio-bando-avviso/?concorso_id={id}"
)

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (DataCivicLab dataset-incubator)",
    "Accept": "application/json",
}

TAG_RE = re.compile(r"<[^>]+>")

REGIONI = {
    "Abruzzo",
    "Basilicata",
    "Calabria",
    "Campania",
    "Emilia-Romagna",
    "Emilia Romagna",
    "Friuli-Venezia Giulia",
    "Lazio",
    "Liguria",
    "Lombardia",
    "Marche",
    "Molise",
    "Piemonte",
    "Puglia",
    "Sardegna",
    "Sicilia",
    "Toscana",
    "Trentino-Alto Adige",
    "Umbria",
    "Valle d'Aosta",
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


def _flatten(item: dict) -> dict:
    item_id = item.get("id")
    return {
        "id": item_id,
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
                (
                    f"{s.get('regioneDenominazione')}-{s.get('provinciaDenominazione')}"
                    if isinstance(s, dict) and s.get("provinciaDenominazione")
                    else s
                )
                for s in (item.get("sedi") or [])
            ],
            sep="|",
        ),
        "salary_min": item.get("salaryMin"),
        "salary_max": item.get("salaryMax"),
        "link_inpa": INPA_LINK_TEMPLATE.format(id=item_id) if item_id else None,
    }


def fetch_page(session: requests.Session, body: dict, page: int, size: int) -> dict:
    resp = session.post(
        SEARCH_ENDPOINT,
        params={"page": page, "size": size},
        json=body,
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()


def harvest_status(
    session: requests.Session,
    status: str,
    size: int,
    pause: float,
    max_items: int | None = None,
) -> list[dict]:
    body = {
        "text": "",
        "categoriaId": None,
        "regioneId": None,
        "status": [status],
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

    first = fetch_page(session, body, page=0, size=size)
    total_elements = first.get("totalElements", 0)
    total_pages = first.get("totalPages", 1)
    print(
        f"inPA {status}: totalElements={total_elements} totalPages={total_pages}", file=sys.stderr
    )

    rows = [_flatten(item) for item in first.get("content", [])]
    if max_items is not None and len(rows) >= max_items:
        rows = rows[:max_items]
    else:
        for page in range(1, total_pages):
            if pause:
                time.sleep(pause)
            data = fetch_page(session, body, page=page, size=size)
            rows.extend(_flatten(item) for item in data.get("content", []))
            if max_items is not None and len(rows) >= max_items:
                rows = rows[:max_items]
                break

    print(f"inPA {status}: raccolti {len(rows)} bandi", file=sys.stderr)
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", help="path del CSV di output")
    parser.add_argument(
        "--status", default="OPEN", help="stato bandi: OPEN o CLOSED (default OPEN)"
    )
    parser.add_argument("--size", type=int, default=500, help="pagine per chiamata (default 500)")
    parser.add_argument("--pause", type=float, default=0.3, help="pausa tra pagine in secondi")
    parser.add_argument(
        "--max-items", type=int, default=None, help="limita il numero di bandi per status (test)"
    )
    args = parser.parse_args()

    session = requests.Session()
    session.headers.update(DEFAULT_HEADERS)

    rows = harvest_status(session, args.status, args.size, args.pause, max_items=args.max_items)

    if not rows:
        print(f"inPA {args.status}: nessun bando raccolto", file=sys.stderr)
        return 1

    out_path = Path(args.output)
    fieldnames = sorted({k for r in rows for k in r})
    with out_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    print(f"inPA {args.status}: scritto {out_path} ({len(rows)} righe)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
