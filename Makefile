PYTHON = python3
TOOLKIT = toolkit
EXPORTS = export TOOLKIT_ALLOW_SCRIPT_SOURCE=1

.PHONY: check run run-all run-bandi run-comunicazioni run-compose clean dashboard harvest-full harvest-daily

check:
	$(TOOLKIT) run preflight -c datasets/inpa-bandi/dataset.yml
	$(TOOLKIT) run preflight -c datasets/inpa-comunicazioni/dataset.yml
	python -m pytest tests/ -v
	ruff check scripts/ dashboard/

run: run-bandi run-comunicazioni run-compose

run-all: run

run-bandi:
	$(EXPORTS) && $(TOOLKIT) run --all -c datasets/inpa-bandi/dataset.yml

run-comunicazioni:
	$(EXPORTS) && $(TOOLKIT) run --all -c datasets/inpa-comunicazioni/dataset.yml

run-compose:
	$(EXPORTS) && $(TOOLKIT) run --all -c compose/inpa-insight/dataset.yml

harvest-full:
	$(PYTHON) datasets/inpa-bandi/scripts/harvest_bandi.py data/raw/bandi_full.csv
	$(PYTHON) datasets/inpa-comunicazioni/scripts/harvest_comunicazioni.py data/raw/comunicazioni_full.csv

harvest-daily:
	$(PYTHON) scripts/harvest_incremental.py

registry:
	$(TOOLKIT) registry build --prefix inpa-reclutamento

registry-write:
	$(TOOLKIT) registry build --prefix inpa-reclutamento --write

dashboard:
	cd dashboard && streamlit run app.py

clean:
	rm -rf out/data/_runs out/data/probe out/data/raw out/data/clean out/data/mart out/data/cross .tmp/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
