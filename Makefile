build:
	docker compose -f local.yml up --build -d --remove-orphans

down:
	docker compose -f local.yml down

down-v:
	docker compose -f local.yml down -v

connect_db:
	docker compose -f local.yml exec postgres psql -U eyram -d nextgen

logs_api:
	docker compose -f local.yml logs api

alembin_upgrade:
	docker compose -f local.yml exec -it api alembic upgrade head

nextgen-config:
	docker compose -f local.yml config

migrations:
	docker compose -f local.yml exec -it api alembic revision --autogenerate -m "$(name)"

migrate:
	docker compose -f local.yml exec -it api alembic upgrade head

history:
	docker compose -f local.yml exec -it api alembic history

current-migration:
	docker compose -f local.yml exec -it api alembic current

downgrade:
	docker compose -f local.yml exec -it api alembic downgrade $(version)

inspect-network:
	docker network inspect nextgen_local_nw