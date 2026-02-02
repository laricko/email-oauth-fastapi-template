dev:
	uv run uvicorn main:app --app-dir src --reload

makemigrations:
	PYTHONPATH=src uv run alembic --config src/alembic.ini revision --autogenerate -m $(message)

migrate:
	PYTHONPATH=src uv run alembic --config src/alembic.ini upgrade head

psql:
	docker exec -it template-postgres psql -U template

redis_cli:
	docker exec -it template-redis redis-cli
