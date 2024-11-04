build:
	docker compose up --build

run:
	docker compose up -d

down:
	docker compose down

migr:
	./src/manage.py makemigrations

restart: down build
