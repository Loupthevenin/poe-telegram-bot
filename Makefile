.PHONY: help build up down restart logs shell test format lint clean

help:
	@echo "Commandes disponibles :"
	@echo "  make build    Construire l'image Docker"
	@echo "  make up       Construire et démarrer le bot"
	@echo "  make down     Arrêter le bot"
	@echo "  make restart  Redémarrer le bot"
	@echo "  make logs     Afficher les logs"
	@echo "  make shell    Ouvrir un shell dans le conteneur"
	@echo "  make test     Lancer les tests"
	@echo "  make format   Formater le code"
	@echo "  make lint     Vérifier le code"
	@echo "  make clean    Supprimer les conteneurs et images du projet"

build:
	docker compose build

up:
	docker compose up -d --build

down:
	docker compose down

restart:
	docker compose restart

logs:
	docker compose logs -f bot

shell:
	docker compose exec bot /bin/bash

test:
	docker compose run --rm bot pytest

format:
	docker compose run --rm bot ruff format src tests

lint:
	docker compose run --rm bot ruff check src tests

clean:
	docker compose down --rmi local --volumes
