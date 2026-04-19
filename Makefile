POETRY := poetry
CSV_DIR := csv
WWW := www
GAME_INSTALL_DIR := "/home/ben/.wine/drive_c/FIFA Soccer Manager"
BASE_URL := https://fsm.bennuttall.com
STATIC_DIR := static

develop:
	pip install poetry
	$(POETRY) install --all-extras --with dev

csv:
	$(POETRY) run fsm-extract ${GAME_INSTALL_DIR}

clean-html:
	rm -rf $(WWW)

html: clean-html
	$(POETRY) run fsm-generate-www --csv-dir ${CSV_DIR} --out-dir ${WWW} --base-url ${BASE_URL}
	cp -r $(STATIC_DIR)/.htaccess $(WWW)/

serve:
	$(POETRY) run python -m http.server -d $(WWW) 8000

.PHONY: develop csv clean-html html serve