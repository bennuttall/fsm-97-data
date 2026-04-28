PYTHON := /home/ben/.virtualenvs/fsm/bin/python
CSV_DIR := csv
WWW := www
GAME_INSTALL_DIR := "/home/ben/.wine/drive_c/FIFA Soccer Manager"
BASE_URL := https://fsm.bennuttall.com
STATIC_DIR := static
LOGS_DIR := logs/apache2
LOGS_CSV_DIR := logs/csv
ANALYTICS_WWW := www-analytics

develop:
	pip install poetry
	poetry install --all-extras --with dev

csv:
	$(PYTHON) -m fsm97.extract ${GAME_INSTALL_DIR}

clean-html:
	rm -rf $(WWW)

html: clean-html
	$(PYTHON) -m fsm97.scribe --csv-dir ${CSV_DIR} --out-dir ${WWW} --base-url ${BASE_URL}

logs:
	$(PYTHON) -m fsm97.logs.cli $(LOGS_DIR) --csv-dir $(LOGS_CSV_DIR)

analytics:
	$(PYTHON) -m fsm97.analytics.cli --csv-dir $(LOGS_CSV_DIR) --manifest $(WWW)/manifest.json --base-url $(BASE_URL)

serve-analytics:
	$(PYTHON) -m http.server -d $(ANALYTICS_WWW) 8001

serve:
	$(PYTHON) -m http.server -d $(WWW) 8000

.PHONY: develop csv clean-html html serve logs analytics serve-analytics
