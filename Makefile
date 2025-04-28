run_dev_local:
	python bunkergame/manage.py runserver

create_migrations:
	python bunkergame/manage.py makemigrations

apply_migrations:
	python bunkergame/manage.py migrate

migrate:
	make create_migrations && make apply_migrations