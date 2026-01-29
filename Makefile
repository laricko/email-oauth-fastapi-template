dev:
	uv run uvicorn main:app --app-dir src --reload

makemigrations:
	PYTHONPATH=src uv run alembic --config src/alembic.ini revision --autogenerate -m $(message)

migrate:
	PYTHONPATH=src uv run alembic --config src/alembic.ini upgrade head

psql:
	docker exec -it mailzen-postgres psql -U mailzen

redis_cli:
	docker exec -it mailzen-redis redis-cli
