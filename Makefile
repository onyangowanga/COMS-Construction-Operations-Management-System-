# Makefile for COMS Project (Linux/Mac)

.PHONY: help setup up down logs shell dbshell migrate superuser test test-cov lint format static clean rebuild backup

help:
	@echo "🏗️  COMS Project Commands"
	@echo ""
	@echo "Setup & Management:"
	@echo "  make setup      - Initial project setup"
	@echo "  make up         - Start all containers"
	@echo "  make down       - Stop all containers"
	@echo "  make rebuild    - Rebuild containers from scratch"
	@echo ""
	@echo "Development:"
	@echo "  make logs       - View web container logs"
	@echo "  make shell      - Open Django shell"
	@echo "  make dbshell    - Open PostgreSQL shell"
	@echo ""
	@echo "Database:"
	@echo "  make migrate    - Run database migrations"
	@echo "  make backup     - Create database backup"
	@echo ""
	@echo "Testing & Quality:"
	@echo "  make test       - Run test suite"
	@echo "  make test-cov   - Run tests with coverage report"
	@echo "  make lint       - Run code linting"
	@echo "  make format     - Format code with Black"
	@echo ""
	@echo "Utilities:"
	@echo "  make superuser  - Create Django superuser"
	@echo "  make static     - Collect static files"
	@echo "  make clean      - Clean up containers and cache"

setup:
	@echo "🔧 Setting up COMS project..."
	@cp -n .env.example .env || true
	@docker-compose build
	@echo "✅ Setup complete!"

up:
	@echo "🚀 Starting COMS containers..."
	@docker-compose up -d
	@echo "✅ Containers started! Visit http://localhost:8000"

down:
	@echo "🛑 Stopping COMS containers..."
	@docker-compose down
	@echo "✅ Containers stopped!"

logs:
	@docker-compose logs -f web

shell:
	@echo "🐚 Opening Django shell..."
	@docker-compose exec web python manage.py shell

dbshell:
	@echo "🗄️ Opening database shell..."
	@docker-compose exec db psql -U coms_user -d coms_db

migrate:
	@echo "🔄 Running migrations..."
	@docker-compose exec web python manage.py makemigrations
	@docker-compose exec web python manage.py migrate
	@echo "✅ Migrations complete!"

superuser:
	@echo "👤 Creating superuser..."
	@docker-compose exec web python manage.py createsuperuser

test:
	@echo "🧪 Running tests..."
	@docker-compose exec web pytest

test-cov:
	@echo "📊 Running tests with coverage..."
	@docker-compose exec web pytest --cov=apps --cov-report=html
	@echo "✅ Coverage report generated in htmlcov/"

lint:
	@echo "🔍 Running linters..."
	@docker-compose exec web pylint apps/

format:
	@echo "✨ Formatting code with Black..."
	@docker-compose exec web black apps/
	@echo "✅ Code formatted!"

static:
	@echo "📦 Collecting static files..."
	@docker-compose exec web python manage.py collectstatic --noinput
	@echo "✅ Static files collected!"

clean:
	@echo "🧹 Cleaning up..."
	@docker-compose down -v
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@rm -rf .pytest_cache htmlcov 2>/dev/null || true
	@echo "✅ Cleanup complete!"

rebuild:
	@echo "🔨 Rebuilding containers..."
	@docker-compose down
	@docker-compose build --no-cache
	@docker-compose up -d
	@echo "✅ Rebuild complete!"

backup:
	@echo "💾 Creating database backup..."
	@mkdir -p backups
	@docker-compose exec -T db pg_dump -U coms_user coms_db > backups/coms_backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "✅ Backup created!"
