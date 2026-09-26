"""Policy and smoke tests for dataset.yml and SQL contracts."""

import pathlib

import pytest

BASE = pathlib.Path(__file__).parent.parent


@pytest.mark.policy
def test_clean_sql_reads_from_raw_input():
    """Verify clean.sql reads only from raw_input."""
    for slug in ["inpa-bandi-open", "inpa-bandi-closed"]:
        sql_path = BASE / "datasets" / slug / "sql" / "clean.sql"
        sql = sql_path.read_text().lower()
        assert "from raw_input" in sql, f"{slug}/clean.sql must read from raw_input"
        assert "raw_input_closed" not in sql, f"{slug}/clean.sql must not reference raw_input_closed"


@pytest.mark.policy
def test_mart_sql_reads_from_clean_input():
    """Verify mart SQL reads only from clean_input or support."""
    for sql_file in (BASE / "datasets" / "inpa-bandi-open" / "sql").glob("mart_*.sql"):
        sql = sql_file.read_text().lower()
        assert "from clean_input" in sql or "read_parquet" in sql, (
            f"{sql_file.name} must read from clean_input or read_parquet"
        )


@pytest.mark.policy
def test_compose_dataset_yml_references_open():
    """Verify compose references inpa-bandi-open (not old inpa-bandi)."""
    import yaml

    cfg = (BASE / "compose" / "inpa-insight" / "dataset.yml").read_text()
    data = yaml.safe_load(cfg)

    support_names = [s["name"] for s in data.get("support", [])]
    assert "bandi" in support_names

    bandi_support = next(s for s in data["support"] if s["name"] == "bandi")
    assert "inpa-bandi-open" in bandi_support["config"]


@pytest.mark.smoke
def test_bandi_open_dataset_yml_fields():
    """Verify inpa-bandi-open dataset.yml has all required fields."""
    import yaml

    cfg = (BASE / "datasets" / "inpa-bandi-open" / "dataset.yml").read_text()
    data = yaml.safe_load(cfg)

    assert data["dataset"]["name"] == "inpa_bandi_open"
    assert data["dataset"]["source_id"] == "inpa_reclutamento"
    assert isinstance(data["dataset"]["years"], list)
    assert len(data["dataset"]["years"]) > 0
    assert data["schema_version"] == 1
    assert "raw" in data
    assert "clean" in data
    assert "sql" in data["clean"]
    assert "required_columns" in data["clean"]
    assert "validate" in data["clean"]


@pytest.mark.smoke
def test_bandi_closed_dataset_yml_fields():
    """Verify inpa-bandi-closed dataset.yml has all required fields."""
    import yaml

    cfg = (BASE / "datasets" / "inpa-bandi-closed" / "dataset.yml").read_text()
    data = yaml.safe_load(cfg)

    assert data["dataset"]["name"] == "inpa_bandi_closed"
    assert data["dataset"]["source_id"] == "inpa_reclutamento"
    assert isinstance(data["dataset"]["years"], list)
    assert data["schema_version"] == 1
    assert "raw" in data
    assert "clean" in data
