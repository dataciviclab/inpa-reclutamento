"""Smoke test for dashboard pages."""

import py_compile
import pathlib


def test_all_pages_compile():
    """Verify all dashboard pages are valid Python."""
    pages_dir = pathlib.Path(__file__).parent.parent / "pages"
    for page in sorted(pages_dir.glob("*.py")):
        py_compile.compile(str(page), doraise=True)


def test_app_compiles():
    """Verify app.py is valid Python."""
    app = pathlib.Path(__file__).parent.parent / "app.py"
    py_compile.compile(str(app), doraise=True)


def test_sources_compiles():
    """Verify sources.py is valid Python."""
    sources = pathlib.Path(__file__).parent.parent / "sources.py"
    py_compile.compile(str(sources), doraise=True)
