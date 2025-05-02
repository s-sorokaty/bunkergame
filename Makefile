run_dev_local:
	python bunkergame/manage.py runserver

run_dev_docker:
	docker compose up -d --build

create_migrations:
	python bunkergame/manage.py makemigrations

apply_migrations:
	python bunkergame/manage.py migrate

migrate:
	make create_migrations && make apply_migrations