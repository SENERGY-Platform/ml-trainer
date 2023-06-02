BINARY_NAME=model-trainer

start_deps:
	docker compose -f deployment/docker-compose.yml up -d flower redis
	
run_api: 
	python -m flask --app model_trainer/server/app run --port=5001

clean:
	docker compose -f deployment/docker-compose.yml down