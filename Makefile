run_api: 
	python -m flask --app model_trainer/app run --port=5001

run_tests:
	pytest

clean:
	docker compose -f deployment/docker-compose.yml down