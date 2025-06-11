.PHONY: start
start: # start bot
	poetry run python launcher.py

.PHONY: fix
fix: # fix code format
	poetry run ruff format
	poetry run ruff check --fix 

.PHONY: setup
setup: # setup tools
	asdf install
	corepack enable
	asdf reshim nodejs
	poetry install

.PHONY: typecheck
typecheck:
	poetry run pyright .

.PHONY: setup-db
setup-db:
	docker compose up -d --build

.PHONY: up-db
up-db:
	docker compose up -d

.PHONY: down-db
down-db:
	docker compose down