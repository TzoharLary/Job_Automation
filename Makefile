.PHONY: install playwright run dev test

PYTHON := /Users/tzoharlary/Documents/Projects/Job_Automation/.venv/bin/python
UVICORN := $(PYTHON) -m uvicorn

install:
	$(PYTHON) -m pip install -r requirements.txt

playwright:
	$(PYTHON) -m playwright install chromium

run:
	$(UVICORN) src.app.main:app --host 0.0.0.0 --port 8000

dev:
	$(UVICORN) src.app.main:app --reload --host 0.0.0.0 --port 8000

test:
	$(PYTHON) -m pytest
