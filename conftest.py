"""pytest configuration — marker registration."""

import pytest


def pytest_configure(config):
    config.addinivalue_line("markers", "contract: contratti pubblici (dataset.yml, parquet schema)")
    config.addinivalue_line("markers", "regression: regressioni già verificate")
    config.addinivalue_line("markers", "smoke: smoke test rapidi")
    config.addinivalue_line("markers", "adapter: test di adattamento")
    config.addinivalue_line("markers", "pure_unit: test puri senza I/O")
    config.addinivalue_line("markers", "policy: policy e vincoli organizzativi")
