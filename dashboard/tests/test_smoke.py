"""Smoke test for dashboard pages."""

import pathlib
import py_compile

import pytest


@pytest.mark.smoke
def test_all_pages_compile():
    """Verify all dashboard pages are valid Python."""
    pages_dir = pathlib.Path(__file__).parent.parent / "pages"
    for page in sorted(pages_dir.glob("*.py")):
        py_compile.compile(str(page), doraise=True)


@pytest.mark.smoke
def test_app_compiles():
    """Verify app.py is valid Python."""
    app = pathlib.Path(__file__).parent.parent / "app.py"
    py_compile.compile(str(app), doraise=True)


@pytest.mark.smoke
def test_sources_compiles():
    """Verify sources.py is valid Python."""
    sources = pathlib.Path(__file__).parent.parent / "sources.py"
    py_compile.compile(str(sources), doraise=True)
