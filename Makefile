POETRY := poetry
WWW := www

develop:
	$(POETRY) install --all-extras --with dev

format:
	isort .
	black .

csv:
	$(POETRY) run fsm-extract

clean-html:
	rm -rf $(WWW)

html: clean-html
	$(POETRY) run fsm-generate-www

serve:
	$(POETRY) run python -m http.server -d $(WWW) 8000

.PHONY: develop format csv clean-html html serve