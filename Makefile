BINARY_NAME=model-trainer

run_api: 
	python -m flask --app model_trainer/server/app run --port=5001

run_tests:
	pytest

clean:
	docker compose -f deployment/docker-compose.yml down