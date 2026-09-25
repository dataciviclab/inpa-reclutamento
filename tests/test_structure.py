"""Structure tests for inPA Reclutamento."""

import pathlib

import pytest


@pytest.mark.contract
def test_datasets_exist():
    """Verify dataset configs exist."""
    base = pathlib.Path(__file__).parent.parent
    assert (base / "datasets" / "inpa-bandi" / "dataset.yml").exists()
    assert (base / "datasets" / "inpa-comunicazioni" / "dataset.yml").exists()
    assert (base / "compose" / "inpa-insight" / "dataset.yml").exists()


@pytest.mark.contract
def test_scripts_exist():
    """Verify harvest scripts exist."""
    base = pathlib.Path(__file__).parent.parent
    assert (base / "scripts" / "harvest_bandi.py").exists()
    assert (base / "scripts" / "harvest_comunicazioni.py").exists()


@pytest.mark.smoke
def test_dashboard_exists():
    """Verify dashboard files exist."""
    base = pathlib.Path(__file__).parent.parent
    assert (base / "dashboard" / "app.py").exists()
    assert (base / "dashboard" / "sources.py").exists()
    assert (base / "dashboard" / "requirements.txt").exists()
    assert (base / "dashboard" / "Dockerfile").exists()
