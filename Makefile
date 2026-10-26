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

.PHONY: test
test:
	poetry run pytest

.PHONY: migrate
migrate: # create a new revision from model diff (make migrate m="reason")
	poetry run alembic revision --autogenerate -m "$(m)"

.PHONY: upgrade
upgrade: # apply pending migrations
	poetry run alembic upgrade head

.PHONY: stamp
stamp: # mark DB as already at head without running DDL (make stamp url="mysql://user:pass@host:port/db")
	poetry run alembic $(if $(url),-x db_url="$(url)") stamp head

.PHONY: downgrade
downgrade: # revert the last migration
	poetry run alembic downgrade -1

.PHONY: migrate-history
migrate-history: # show revision history and current version
	poetry run alembic history
	poetry run alembic current