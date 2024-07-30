run_api: 
	fastapi dev model_trainer/app.py --port=5001

run_tests:
	pytest

clean:
	docker compose -f deployment/docker-compose.yml down