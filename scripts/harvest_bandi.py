#!/usr/bin/env python3
"""Harvest bandi dal Portale inPA (Portale del Reclutamento PA).

Chiama l'API pubblica non documentata ``concorsi-smart`` di inPA e produce un
CSV flat dei bandi.

Uso:
    python3 harvest_bandi.py <output.csv> --status OPEN     # ~30s
    python3 harvest_bandi.py <output.csv> --status CLOSED   # ~15-20min (API lenta)
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
from concurrent.futures import ThreadPoolExecutor, as_completed
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

# L'API torna 500 intermittente su pagine profonde: max 3 tentativi con backoff.
MAX_RETRIES = 3
RETRY_BACKOFF = 2.0

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
    """POST una pagina con retry: l'API inPA torna 500 intermittente sulle pagine profonde."""
    last_exc: Exception | None = None
    for attempt in range(MAX_RETRIES):
        try:
            resp = session.post(
                SEARCH_ENDPOINT,
                params={"page": page, "size": size},
                json=body,
                timeout=90,
            )
            # 500 = errore interno transitorio dell'API, non un dato mancante
            if resp.status_code >= 500:
                last_exc = requests.HTTPError(f"HTTP {resp.status_code} on page={page}")
            else:
                resp.raise_for_status()
                return resp.json()
        except requests.RequestException as exc:
            last_exc = exc
        if attempt < MAX_RETRIES - 1:
            wait = RETRY_BACKOFF * (attempt + 1)
            print(
                f"inPA: pagina {page} fallita (tentativo {attempt + 1}/{MAX_RETRIES}), "
                f"riprovo tra {wait:.0f}s…",
                file=sys.stderr,
            )
            time.sleep(wait)
    raise RuntimeError(f"inPA: pagina {page} non recuperabile dopo {MAX_RETRIES} tentativi") from last_exc


def harvest_status(
    session: requests.Session,
    status: str,
    size: int,
    pause: float,
    max_items: int | None = None,
    workers: int = 3,
) -> list[dict]:
    """Raccoglie i bandi per status.

    Con workers > 1 le pagine successive alla prima sono fetchate in parallelo:
    l'API è lenta (~10-40s a pagina per CLOSED) ma accetta 3 richieste
    concorrenti senza rate-limit. Il primo fetch (sync) serve per scoprire
    totalElements/totalPages.
    """
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
        f"inPA {status}: totalElements={total_elements} totalPages={total_pages} "
        f"workers={workers}",
        file=sys.stderr,
    )

    rows = [_flatten(item) for item in first.get("content", [])]
    if max_items is not None and len(rows) >= max_items:
        return rows[:max_items]

    remaining = list(range(1, total_pages))
    if workers <= 1:
        for page in remaining:
            if pause:
                time.sleep(pause)
            data = fetch_page(session, body, page=page, size=size)
            rows.extend(_flatten(item) for item in data.get("content", []))
            if max_items is not None and len(rows) >= max_items:
                return rows[:max_items]
    else:
        # Session non è thread-safe: una sessione per worker
        def _fetch_one(page: int) -> list[dict]:
            local = requests.Session()
            local.headers.update(DEFAULT_HEADERS)
            if pause:
                time.sleep(pause * (page % workers))
            data = fetch_page(local, body, page=page, size=size)
            return [_flatten(item) for item in data.get("content", [])]

        done = 0
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {pool.submit(_fetch_one, p): p for p in remaining}
            for fut in as_completed(futures):
                page = futures[fut]
                rows.extend(fut.result())
                done += 1
                if done % 10 == 0 or done == len(remaining):
                    print(
                        f"inPA {status}: {done}/{len(remaining)} pagine, {len(rows)} bandi",
                        file=sys.stderr,
                    )
                if max_items is not None and len(rows) >= max_items:
                    pool.shutdown(wait=False, cancel_futures=True)
                    return rows[:max_items]

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
        "--workers",
        type=int,
        default=3,
        help="thread paralleli per il fetch delle pagine (default 3, 1 = sequenziale)",
    )
    parser.add_argument(
        "--max-items", type=int, default=None, help="limita il numero di bandi per status (test)"
    )
    args = parser.parse_args()

    session = requests.Session()
    session.headers.update(DEFAULT_HEADERS)

    rows = harvest_status(
        session,
        args.status,
        args.size,
        args.pause,
        max_items=args.max_items,
        workers=max(1, args.workers),
    )

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
