build:
	docker compose -f local.yml up --build -d --remove-orphans

down:
	docker compose -f local.yml down

down-v:
	docker compose -f local.yml down -v

connect_db:
	docker compose -f local.yml exec postgres psql -U eyram -d nextgen