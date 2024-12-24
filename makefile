.PHONY: setup format types migration start build up down test deploy install

format:
	@echo "formatting..."
	poetry run ruff format app

types:
	@echo "checking types..."
	poetry run mypy app

migration:
	@echo "running migrations..."
	alembic revision --autogenerate -m "initial migration"

#poetry run python app/main.py
start:
	@echo "starting app..."
	poetry run cli.py api


build:
	docker-compose -f "docker/docker-compose.yml" build

up:
	docker-compose -f "docker/docker-compose.yml" up -d

up-db:
	@echo "Starting PostgreSQL in Docker..."
	docker-compose -f "docker/docker-compose.yml" up -d db

down:
	docker-compose -f "docker/docker-compose.yml" down

test:
	docker-compose -f "docker/docker-compose.yml" run api pytest

deploy:
	# Команды для деплоя

install:
	@echo "installing dependencies..."
	pip install poetry
	poetry lock
	poetry install
	@echo "Setting up the application..."
	docker-compose -f "docker/docker-compose.yml" up --build -d

cli-api:
	@echo "Starting PostgreSQL in Docker..."
	docker-compose -f "docker/docker-compose.yml" up -d db
	@echo "Starting FastAPI locally..."
	poetry run python cli.py api

setup: install