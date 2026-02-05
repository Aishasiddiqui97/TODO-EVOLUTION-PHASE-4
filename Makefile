# Makefile for Event-Driven Todo Chatbot - Phase V MVP

.PHONY: help install build deploy-local deploy-k8s test clean

help:
	@echo "Event-Driven Todo Chatbot - Phase V MVP"
	@echo "========================================"
	@echo ""
	@echo "Available commands:"
	@echo "  make install        - Install dependencies"
	@echo "  make build          - Build Docker image"
	@echo "  make deploy-local   - Deploy with Docker Compose"
	@echo "  make deploy-k8s     - Deploy to Kubernetes"
	@echo "  make test           - Run API tests"
	@echo "  make clean          - Clean up resources"
	@echo "  make logs           - View logs"
	@echo "  make status         - Check deployment status"

install:
	@echo "Installing dependencies..."
	pip install -r backend/requirements.txt

build:
	@echo "Building Docker image..."
	docker build -t chat-api:latest -f backend/Dockerfile .

deploy-local:
	@echo "Deploying with Docker Compose..."
	@if [ ! -f backend/.env ]; then \
		echo "Creating .env file from template..."; \
		cp backend/.env.example backend/.env; \
		echo "Please edit backend/.env and add your OPENAI_API_KEY"; \
		exit 1; \
	fi
	docker-compose up -d
	@echo "Waiting for services to be ready..."
	@sleep 10
	@echo "Services deployed!"
	@echo "Chat API: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"

deploy-k8s:
	@echo "Deploying to Kubernetes..."
	@if command -v minikube > /dev/null; then \
		bash deploy-local.sh; \
	else \
		echo "Minikube not found. Please install Minikube."; \
		exit 1; \
	fi

test:
	@echo "Running API tests..."
	@if command -v bash > /dev/null; then \
		bash test-api.sh; \
	else \
		echo "Bash not found. Please run test-api.sh manually."; \
	fi

clean:
	@echo "Cleaning up resources..."
	docker-compose down -v
	@if command -v kubectl > /dev/null; then \
		kubectl delete -f k8s/services/ --ignore-not-found=true; \
		kubectl delete -f k8s/dapr/ --ignore-not-found=true; \
		kubectl delete -f k8s/local/ --ignore-not-found=true; \
	fi
	@echo "Cleanup complete!"

logs:
	@echo "Viewing logs..."
	@if docker-compose ps | grep -q chat-api; then \
		docker-compose logs -f chat-api; \
	elif command -v kubectl > /dev/null && kubectl get deployment chat-api > /dev/null 2>&1; then \
		kubectl logs -f deployment/chat-api -c chat-api; \
	else \
		echo "No deployment found."; \
	fi

status:
	@echo "Checking deployment status..."
	@echo ""
	@echo "Docker Compose:"
	@docker-compose ps || echo "Not running"
	@echo ""
	@echo "Kubernetes:"
	@kubectl get pods -l app=chat-api 2>/dev/null || echo "Not deployed"
	@echo ""
	@echo "Health Check:"
	@curl -s http://localhost:8000/health 2>/dev/null || echo "Not accessible"

port-forward:
	@echo "Setting up port forwarding..."
	kubectl port-forward svc/chat-api 8000:8000

# Development commands
dev-install:
	@echo "Installing development dependencies..."
	pip install -r backend/requirements.txt
	pip install pytest pytest-asyncio httpx

dev-run:
	@echo "Running development server..."
	cd backend && uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

dev-test:
	@echo "Running unit tests..."
	pytest backend/tests/

# Docker commands
docker-build:
	docker build -t chat-api:latest -f backend/Dockerfile .

docker-run:
	docker run -p 8000:8000 --env-file backend/.env chat-api:latest

docker-push:
	@echo "Pushing to registry..."
	@read -p "Enter registry URL: " registry; \
	docker tag chat-api:latest $$registry/chat-api:latest; \
	docker push $$registry/chat-api:latest

# Kubernetes commands
k8s-apply:
	kubectl apply -f k8s/local/
	kubectl apply -f k8s/dapr/
	kubectl apply -f k8s/services/

k8s-delete:
	kubectl delete -f k8s/services/
	kubectl delete -f k8s/dapr/
	kubectl delete -f k8s/local/

k8s-logs:
	kubectl logs -f deployment/chat-api -c chat-api

k8s-describe:
	kubectl describe deployment chat-api

k8s-restart:
	kubectl rollout restart deployment/chat-api

# Dapr commands
dapr-init:
	dapr init -k

dapr-status:
	dapr status -k

dapr-dashboard:
	dapr dashboard -k

# Database commands
db-connect:
	@if docker-compose ps | grep -q postgres; then \
		docker-compose exec db psql -U todouser -d todoapp; \
	elif command -v kubectl > /dev/null && kubectl get pod -l app=postgres > /dev/null 2>&1; then \
		kubectl exec -it deployment/postgres -- psql -U todouser -d todoapp; \
	else \
		echo "Database not found."; \
	fi

# Kafka commands
kafka-topics:
	@if docker-compose ps | grep -q redpanda; then \
		docker-compose exec redpanda rpk topic list; \
	elif command -v kubectl > /dev/null && kubectl get pod -l app=redpanda > /dev/null 2>&1; then \
		kubectl exec -it deployment/redpanda -- rpk topic list; \
	else \
		echo "Kafka not found."; \
	fi

kafka-consume:
	@if docker-compose ps | grep -q redpanda; then \
		docker-compose exec redpanda rpk topic consume task-events; \
	elif command -v kubectl > /dev/null && kubectl get pod -l app=redpanda > /dev/null 2>&1; then \
		kubectl exec -it deployment/redpanda -- rpk topic consume task-events; \
	else \
		echo "Kafka not found."; \
	fi
