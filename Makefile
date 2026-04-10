POETRY := poetry

develop:
	$(POETRY) install --all-extras --with dev

format:
	isort .
	black .

csv:
	$(POETRY) run fsm-extract

html:
	$(POETRY) run fsm-generate-www

serve:
	$(POETRY) run python -m http.server -d www

.PHONY: develop format csv html serve