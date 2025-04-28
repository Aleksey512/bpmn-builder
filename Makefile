.PHONY: help frontend-dev backend-dev infra-dev without-ml ml-cpu-dev ml-gpu-dev dev-all-cpu dev-all-gpu

COMPOSE_DIR=./deploy/dev
ENV_FILE=$(COMPOSE_DIR)/.env

COMPOSE_CMD=docker compose --env-file $(ENV_FILE)

.DEFAULT_GOAL := help

help:
	@echo "❌ Ничего не произошло. Используйте одну из доступных команд:"
	@bash ./scripts/makefile-help.sh

## Копирует .env файл если он существует
copy-env:
	@if [ -f .env ]; then \
		echo "📋 Копирую .env в $(ENV_FILE)"; \
		cp .env $(ENV_FILE); \
	else \
		echo "⚠️ Файл .env не найден в корне проекта"; \
	fi

## Создает dev frontend
frontend-dev: copy-env
	$(COMPOSE_CMD) \
		-f $(COMPOSE_DIR)/docker-compose.frontend.yml up -d --build --force-recreate

## Создает dev backend
backend-dev: copy-env
	$(COMPOSE_CMD) \
		-f $(COMPOSE_DIR)/docker-compose.backend.yml up -d --build --force-recreate

## Создает dev infrastructure (postgres, redis etc...)
infra-dev: copy-env
	$(COMPOSE_CMD) \
		-f $(COMPOSE_DIR)/docker-compose.infra.yml up -d --build --force-recreate

## Запуск приложения без ML сервисов
without-ml: copy-env
	$(COMPOSE_CMD) \
		-f $(COMPOSE_DIR)/docker-compose.frontend.yml \
		-f $(COMPOSE_DIR)/docker-compose.backend.yml \
		-f $(COMPOSE_DIR)/docker-compose.infra.yml \
		up -d --build --force-recreate

## Запускает ML сервисы в dev режиме (CPU)
ml-cpu-dev: copy-env
	$(COMPOSE_CMD) \
		-f $(COMPOSE_DIR)/docker-compose.ml.yml up -d --build --force-recreate

# Запускает ML сервисы в dev режиме (GPU)
ml-gpu-dev: copy-env
	$(COMPOSE_CMD) \
		-f $(COMPOSE_DIR)/docker-compose.ml.yml \
		-f $(COMPOSE_DIR)/docker-compose.ml.gpu.yml \
		up -d --build --force-recreate

## Запускает все сервисы (frontend, backend, ML) в dev режиме (CPU)
dev-all-cpu: copy-env
	$(COMPOSE_CMD) \
		-f $(COMPOSE_DIR)/docker-compose.frontend.yml \
		-f $(COMPOSE_DIR)/docker-compose.backend.yml \
		-f $(COMPOSE_DIR)/docker-compose.infra.yml \
		-f $(COMPOSE_DIR)/docker-compose.ml.yml \
		up -d --build --force-recreate

## Запускает все сервисы (frontend, backend, ML) в dev режиме (GPU)
dev-all-gpu: copy-env
	$(COMPOSE_CMD) \
		-f $(COMPOSE_DIR)/docker-compose.frontend.yml \
		-f $(COMPOSE_DIR)/docker-compose.backend.yml \
		-f $(COMPOSE_DIR)/docker-compose.infra.yml \
		-f $(COMPOSE_DIR)/docker-compose.ml.yml \
		-f $(COMPOSE_DIR)/docker-compose.ml.gpu.yml \
		up -d --build --force-recreate
