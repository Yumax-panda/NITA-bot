.PHONY: start
start: # start bot
	poetry run python launcher.py

.PHONY: fix
fix: # fix code format
	poetry run ruff check --fix 
	poetry run ruff format