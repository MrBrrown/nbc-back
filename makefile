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

start:
	@echo "starting app..."
	poetry run python app/main.py

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

test:
	docker-compose run api pytest

deploy:
	# Команды для деплоя

install:
	@echo "installing dependencies..."
	pip install poetry
	poetry lock
	poetry install

setup: install start

install:
	@echo "Setting up the application..."
	docker-compose up -d
	@echo "Installing dependencies..."
	poetry lock
	poetry install