.PHONY: start
start: # start bot
	poetry run python launcher.py

.PHONY: fix
fix: # fix code format
	poetry run ruff check --fix 
	poetry run ruff format

.PHONY: setup
setup: # setup tools
	asdf install
	corepack enable
	asdf reshim nodejs
	poetry install

.PHONY: typecheck
typecheck:
	poetry run pyright .