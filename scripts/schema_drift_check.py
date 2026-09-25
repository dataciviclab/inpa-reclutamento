#!/usr/bin/env python3
"""Verifica che le colonne raw CSV non siano cambiate rispetto allo schema atteso.

Legge l'ultima riga di un CSV e confronta le colonne con lo schema definito.
Utile per rilevare drift nell'API inPA.

Uso:
    python3 scripts/schema_drift_check.py data/raw/bandi_daily.csv --schema bandi
    python3 scripts/schema_drift_check.py data/raw/comunicazioni_daily.csv --schema comunicazioni
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

# Schema atteso per i CSV raw
SCHEMAS = {
    "bandi": {
        "required": {
            "id",
            "codice",
            "titolo",
            "dataPubblicazione",
            "dataScadenza",
            "calculatedStatus",
            "tipoProcedura",
            "numPosti",
            "figuraRicercata",
            "dataVisibilita",
        },
        "optional": {
            "descrizioneBreve",
            "descrizione",
            "statusLabel",
            "categorie",
            "settori",
            "sedi",
            "entiRiferimento",
            # Fields from detail endpoint
            "companyDistrictCode",
            "linkSitoPA",
            "emailReferente",
            "richiedePagamento",
            "pecObbligatoria",
            "isRemote",
            "salaryMin",
            "salaryMax",
            "linkGazzettaUfficiale",
            "allegati",
        },
    },
    "comunicazioni": {
        "required": {
            "id",
            "concorsoId",
            "concorsoTitle",
            "subject",
            "categoryName",
            "dateFirstPublish",
            "companyName",
        },
        "optional": {"body"},
    },
}


def check_csv(path: Path, schema_name: str, verbose: bool) -> bool:
    """Controlla le colonne del CSV contro lo schema."""
    schema = SCHEMAS.get(schema_name)
    if not schema:
        print(
            f"FAIL: schema sconosciuto '{schema_name}'. Disponibili: {list(SCHEMAS)}",
            file=sys.stderr,
        )
        return False

    if not path.exists():
        print(f"FAIL: file non trovato {path}", file=sys.stderr)
        return False

    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        columns = set(reader.fieldnames or [])

    if verbose:
        print(f"Colonne trovate ({len(columns)}): {sorted(columns)}")

    # Check required
    missing_required = schema["required"] - columns
    if missing_required:
        print(f"FAIL: colonne obbligatorie mancanti: {missing_required}", file=sys.stderr)
        return False

    # Check for new unexpected columns
    known = schema["required"] | schema["optional"]
    new_columns = columns - known
    if new_columns and verbose:
        print(f"WARNING: nuove colonne non nello schema: {sorted(new_columns)}")

    if verbose:
        print(
            f"OK: {schema_name} — {len(columns)} colonne, {len(schema['required'])} obbligatorie presenti"
        )

    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", type=Path, help="path del CSV raw")
    parser.add_argument(
        "--schema", required=True, choices=list(SCHEMAS.keys()), help="schema da confrontare"
    )
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    ok = check_csv(args.csv_path, args.schema, args.verbose)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
