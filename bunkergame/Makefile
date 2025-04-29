create_migrations:
	poetry run python manage.py makemigrations

apply_migrations:
	poetry run python manage.py migrate

migrate:
	make create_migrations && make apply_migrations