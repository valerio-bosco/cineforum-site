.PHONY: help build up down logs restart clean migrate superuser test

help:
	@echo "Cineforum Management Commands"
	@echo "=============================="
	@echo "build          - Build all Docker images"
	@echo "up             - Start all services"
	@echo "down           - Stop all services"
	@echo "logs           - View logs from all services"
	@echo "restart        - Restart all services"
	@echo "clean          - Remove all containers, volumes, and images"
	@echo "migrate        - Run Django migrations"
	@echo "superuser      - Create Django superuser"
	@echo "shell          - Open Django shell"
	@echo "test           - Run tests"
	@echo "k8s-deploy     - Deploy to Kubernetes"
	@echo "k8s-delete     - Delete Kubernetes deployment"

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "Services starting..."
	@echo "Frontend: http://localhost:3000"
	@echo "Backend API: http://localhost:8000/api"
	@echo "Django Admin: http://localhost:8000/admin"

down:
	docker-compose down

logs:
	docker-compose logs -f

restart:
	docker-compose restart

clean:
	docker-compose down -v --rmi all
	@echo "All containers, volumes, and images removed"

migrate:
	docker-compose exec backend python manage.py makemigrations
	docker-compose exec backend python manage.py migrate

superuser:
	docker-compose exec backend python manage.py createsuperuser

shell:
	docker-compose exec backend python manage.py shell

test:
	docker-compose exec backend python manage.py test

k8s-deploy:
	kubectl apply -f kubernetes/deployment.yaml
	@echo "Kubernetes deployment created"
	@echo "Check status with: kubectl get pods -n cineforum"

k8s-delete:
	kubectl delete -f kubernetes/deployment.yaml
	@echo "Kubernetes deployment deleted"

k8s-logs:
	kubectl logs -n cineforum -l app=backend --tail=100 -f