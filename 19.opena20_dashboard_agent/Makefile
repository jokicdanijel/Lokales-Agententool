.PHONY: help build up down logs preflight deploy clean

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

preflight:  ## Run preflight checks
	@echo "🔍 Running preflight checks..."
	@python3 scripts/preflight_check.py

build:  ## Build all Docker images
	@echo "🔨 Building Docker images..."
	@docker-compose build

up:  ## Start all services
	@echo "🚀 Starting services..."
	@docker-compose up -d
	@echo "✅ Services started"
	@make status

down:  ## Stop all services
	@echo "🛑 Stopping services..."
	@docker-compose down

logs:  ## Show logs (usage: make logs SERVICE=auth)
	@docker-compose logs -f $(SERVICE)

status:  ## Show service status
	@echo "📊 Service Status:"
	@docker-compose ps

deploy:  preflight build up  ## Full deployment (preflight + build + start)
	@echo "🎉 Deployment complete!"

clean:   ## Clean up containers and volumes
	@echo "🧹 Cleaning up..."
	@docker-compose down -v
	@docker system prune -f

restart:   ## Restart all services
	@make down
	@make up

shell:  ## Open shell in service (usage: make shell SERVICE=auth)
	@docker-compose exec $(SERVICE) /bin/sh

db-shell:  ## Open PostgreSQL shell
	@docker-compose exec postgres psql -U eden_user -d eden

redis-cli:  ## Open Redis CLI
	@docker-compose exec redis redis-cli -a $(REDIS_PASSWORD)

backup-db:  ## Backup database
	@echo "💾 Backing up database..."
	@docker-compose exec -T postgres pg_dump -U eden_user eden > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "✅ Backup complete"

restore-db:  ## Restore database (usage: make restore-db FILE=backup.sql)
	@echo "📥 Restoring database..."
	@docker-compose exec -T postgres psql -U eden_user eden < $(FILE)
	@echo "✅ Restore complete"
