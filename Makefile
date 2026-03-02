PYTHON ?= python3
VENV_DIR ?= .venv
VENV_PYTHON := $(VENV_DIR)/bin/python
VENV_PIP := $(VENV_DIR)/bin/pip

.PHONY: setup install run-backend run-frontend dev clean-venv

setup: $(VENV_PYTHON)
	$(VENV_PIP) install --upgrade pip
	$(VENV_PIP) install -r requirements.txt

install: setup

$(VENV_PYTHON):
	$(PYTHON) -m venv $(VENV_DIR)

run-backend:
	$(VENV_PYTHON) -m uvicorn app.main:app --reload

run-frontend:
	cd frontend && $(PYTHON) -m http.server 5500

dev:
	@echo "Starting backend and frontend in parallel..."
	@trap 'kill 0' INT TERM; \
	$(MAKE) run-backend & \
	$(MAKE) run-frontend & \
	wait

clean-venv:
	rm -rf $(VENV_DIR)
