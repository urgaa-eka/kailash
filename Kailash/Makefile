# Kailash developer Makefile

PY ?= python
PLATFORM_SERVICES := document-ai forecasting anomaly rag vision-gateway speech model-registry knowledge-graph automobile-llm
COMPOSE := docker compose -f docker-compose.yml

.PHONY: help install test test-platform lint fmt up down logs ps clean

help:
	@echo "Targets:"
	@echo "  install          install backend requirements"
	@echo "  test             run backend tests"
	@echo "  test-platform    run platform service tests"
	@echo "  lint             ruff check"
	@echo "  fmt              ruff format"
	@echo "  up / down / logs docker compose"

install:
	$(PY) -m pip install -r backend/requirements.txt
	$(PY) -m pip install pytest httpx

test:
	$(PY) -m pytest -q tests/

test-platform:
	@for s in $(PLATFORM_SERVICES); do \
		echo "::group::$$s"; \
		( cd backend/services/$$s && $(PY) -m pytest -q ) || exit $$?; \
		echo "::endgroup::"; \
	done

lint:
	$(PY) -m ruff check backend

fmt:
	$(PY) -m ruff format backend

up:
	$(COMPOSE) up -d --build

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f

ps:
	$(COMPOSE) ps

clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -prune -exec rm -rf {} + 2>/dev/null || true
