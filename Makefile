PYTHON = python3
TOOLKIT = toolkit
EXPORTS = export TOOLKIT_ALLOW_SCRIPT_SOURCE=1

.PHONY: check run run-all run-bandi run-bandi-open run-bandi-closed run-comunicazioni run-compose clean dashboard health-check schema-check

check:
	$(TOOLKIT) run preflight -c datasets/inpa-bandi-open/dataset.yml
	$(TOOLKIT) run preflight -c datasets/inpa-bandi-closed/dataset.yml
	$(TOOLKIT) run preflight -c datasets/inpa-comunicazioni/dataset.yml
	python -m pytest tests/ -v
	ruff check scripts/ dashboard/

health-check:
	$(PYTHON) scripts/source_health_check.py --verbose

schema-check:
	$(PYTHON) scripts/schema_drift_check.py data/raw/bandi_open.csv --schema bandi --verbose

run: run-bandi run-comunicazioni run-compose

run-all: run

run-bandi: run-bandi-open run-bandi-closed

run-bandi-open:
	$(EXPORTS) && $(TOOLKIT) run -c datasets/inpa-bandi-open/dataset.yml

run-bandi-closed:
	$(EXPORTS) && $(TOOLKIT) run -c datasets/inpa-bandi-closed/dataset.yml

run-comunicazioni:
	$(EXPORTS) && $(TOOLKIT) run -c datasets/inpa-comunicazioni/dataset.yml

run-compose:
	$(EXPORTS) && $(TOOLKIT) run -c compose/inpa-insight/dataset.yml

dashboard:
	cd dashboard && streamlit run app.py

clean:
	rm -rf out/data/_runs out/data/probe out/data/raw out/data/clean out/data/mart out/data/cross .tmp/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
