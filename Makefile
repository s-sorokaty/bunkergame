TEST_CONTAINER_NAME=bunckergame_test

run_dev_local:
	python bunkergame/manage.py runserver

run_dev_docker:
	docker compose up -d --build

run_docker_migrate:
	docker run --env-file ${PWD}/bunkergame/.env -v ${PWD}/bunkergame/:/bunkergame/ bunckergame-buncker-game-server:latest /bin/bash -c 'make migrate' 

run_docker_test:
	@if [ "$$(docker ps -aq -f name=$(TEST_CONTAINER_NAME))" ]; then \
		echo "Deleting container: $(TEST_CONTAINER_NAME)"; \
		docker rm -f $(TEST_CONTAINER_NAME); \
	else \
		echo "Container $(TEST_CONTAINER_NAME) does not exist."; \
	fi

	docker run --name $(TEST_CONTAINER_NAME) --env-file ${PWD}/bunkergame/.env -v ${PWD}/bunkergame/:/bunkergame/ bunckergame-buncker-game-server:latest /bin/bash -c 'poetry run python manage.py test'  