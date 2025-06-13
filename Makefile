# Makefile para o projeto Havoc

.PHONY: help build up down logs shell migrate collectstatic createsuperuser test clean

# Variáveis
DOCKER_COMPOSE = docker-compose
DOCKER_COMPOSE_DEV = docker-compose -f docker-compose.dev.yml
DOCKER_COMPOSE_PROD = docker-compose -f docker-compose.yml

# Cores para output
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[0;33m
BLUE = \033[0;34m
NC = \033[0m # No Color

help: ## Mostra esta ajuda
	@echo "$(BLUE)Comandos disponíveis para o projeto Havoc:$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

# =============================================================================
# COMANDOS DE DESENVOLVIMENTO
# =============================================================================

dev-build: ## Constrói as imagens para desenvolvimento
	@echo "$(YELLOW)Construindo imagens para desenvolvimento...$(NC)"
	$(DOCKER_COMPOSE_DEV) build

dev-up: ## Inicia os serviços em modo desenvolvimento
	@echo "$(YELLOW)Iniciando serviços em modo desenvolvimento...$(NC)"
	$(DOCKER_COMPOSE_DEV) up -d

dev-down: ## Para os serviços de desenvolvimento
	@echo "$(YELLOW)Parando serviços de desenvolvimento...$(NC)"
	$(DOCKER_COMPOSE_DEV) down

dev-logs: ## Mostra os logs dos serviços de desenvolvimento
	$(DOCKER_COMPOSE_DEV) logs -f

dev-shell: ## Acessa o shell do container web em desenvolvimento
	$(DOCKER_COMPOSE_DEV) exec web bash

dev-django-shell: ## Acessa o shell do Django em desenvolvimento
	$(DOCKER_COMPOSE_DEV) exec web python manage.py shell

dev-migrate: ## Executa migrações em desenvolvimento
	$(DOCKER_COMPOSE_DEV) exec web python manage.py migrate

dev-makemigrations: ## Cria migrações em desenvolvimento
	$(DOCKER_COMPOSE_DEV) exec web python manage.py makemigrations

dev-createsuperuser: ## Cria superusuário em desenvolvimento
	$(DOCKER_COMPOSE_DEV) exec web python manage.py createsuperuser

dev-test: ## Executa testes em desenvolvimento
	$(DOCKER_COMPOSE_DEV) exec web python manage.py test

dev-collectstatic: ## Coleta arquivos estáticos em desenvolvimento
	$(DOCKER_COMPOSE_DEV) exec web python manage.py collectstatic --noinput

# =============================================================================
# COMANDOS DE PRODUÇÃO
# =============================================================================

build: ## Constrói as imagens para produção
	@echo "$(YELLOW)Construindo imagens para produção...$(NC)"
	$(DOCKER_COMPOSE_PROD) build

up: ## Inicia os serviços em modo produção
	@echo "$(YELLOW)Iniciando serviços em modo produção...$(NC)"
	$(DOCKER_COMPOSE_PROD) up -d

down: ## Para os serviços de produção
	@echo "$(YELLOW)Parando serviços de produção...$(NC)"
	$(DOCKER_COMPOSE_PROD) down

logs: ## Mostra os logs dos serviços de produção
	$(DOCKER_COMPOSE_PROD) logs -f

shell: ## Acessa o shell do container web em produção
	$(DOCKER_COMPOSE_PROD) exec web bash

django-shell: ## Acessa o shell do Django em produção
	$(DOCKER_COMPOSE_PROD) exec web python manage.py shell

migrate: ## Executa migrações em produção
	$(DOCKER_COMPOSE_PROD) exec web python manage.py migrate

collectstatic: ## Coleta arquivos estáticos em produção
	$(DOCKER_COMPOSE_PROD) exec web python manage.py collectstatic --noinput

createsuperuser: ## Cria superusuário em produção
	$(DOCKER_COMPOSE_PROD) exec web python manage.py createsuperuser

# =============================================================================
# COMANDOS DE MANUTENÇÃO
# =============================================================================

restart: ## Reinicia todos os serviços
	@echo "$(YELLOW)Reiniciando serviços...$(NC)"
	$(DOCKER_COMPOSE_PROD) restart

restart-web: ## Reinicia apenas o serviço web
	$(DOCKER_COMPOSE_PROD) restart web

restart-celery: ## Reinicia os serviços do Celery
	$(DOCKER_COMPOSE_PROD) restart celery_worker celery_beat

status: ## Mostra o status dos serviços
	$(DOCKER_COMPOSE_PROD) ps

health: ## Verifica a saúde dos serviços
	@echo "$(BLUE)Verificando saúde dos serviços...$(NC)"
	@curl -f http://localhost:8000/health/ || echo "$(RED)Web service não está saudável$(NC)"
	@curl -f http://localhost:5555/ || echo "$(RED)Flower não está acessível$(NC)"

backup-db: ## Faz backup do banco de dados
	@echo "$(YELLOW)Fazendo backup do banco de dados...$(NC)"
	$(DOCKER_COMPOSE_PROD) exec db pg_dump -U postgres havoc_prod > backup_$(shell date +%Y%m%d_%H%M%S).sql

restore-db: ## Restaura backup do banco de dados (use: make restore-db FILE=backup.sql)
	@echo "$(YELLOW)Restaurando backup do banco de dados...$(NC)"
	$(DOCKER_COMPOSE_PROD) exec -T db psql -U postgres havoc_prod < $(FILE)

# =============================================================================
# COMANDOS DE LIMPEZA
# =============================================================================

clean: ## Remove containers, volumes e imagens não utilizados
	@echo "$(YELLOW)Limpando recursos Docker...$(NC)"
	docker system prune -f
	docker volume prune -f

clean-all: ## Remove TODOS os containers, volumes e imagens
	@echo "$(RED)ATENÇÃO: Isso removerá TODOS os dados!$(NC)"
	@read -p "Tem certeza? [y/N] " -n 1 -r; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo ""; \
		$(DOCKER_COMPOSE_PROD) down -v --rmi all; \
		docker system prune -af; \
	else \
		echo ""; \
		echo "Operação cancelada."; \
	fi

# =============================================================================
# COMANDOS DE DEPLOY
# =============================================================================

deploy: ## Deploy completo (build + up + migrate + collectstatic)
	@echo "$(GREEN)Iniciando deploy...$(NC)"
	$(MAKE) build
	$(MAKE) up
	@echo "$(YELLOW)Aguardando serviços...$(NC)"
	sleep 30
	$(MAKE) migrate
	$(MAKE) collectstatic
	@echo "$(GREEN)Deploy concluído!$(NC)"

quick-deploy: ## Deploy rápido (apenas restart)
	@echo "$(GREEN)Deploy rápido...$(NC)"
	$(DOCKER_COMPOSE_PROD) pull
	$(DOCKER_COMPOSE_PROD) up -d --force-recreate
	@echo "$(GREEN)Deploy rápido concluído!$(NC)"

# =============================================================================
# COMANDOS DE MONITORAMENTO
# =============================================================================

monitor: ## Mostra estatísticas dos containers
	@echo "$(BLUE)Estatísticas dos containers:$(NC)"
	docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"

top: ## Mostra processos dos containers
	$(DOCKER_COMPOSE_PROD) top

# =============================================================================
# COMANDOS DE DESENVOLVIMENTO ESPECÍFICOS
# =============================================================================

format: ## Formata o código com black e isort
	@echo "$(YELLOW)Formatando código...$(NC)"
	$(DOCKER_COMPOSE_DEV) exec web black .
	$(DOCKER_COMPOSE_DEV) exec web isort .

lint: ## Executa linting com flake8
	@echo "$(YELLOW)Executando linting...$(NC)"
	$(DOCKER_COMPOSE_DEV) exec web flake8 .

test-coverage: ## Executa testes com cobertura
	@echo "$(YELLOW)Executando testes com cobertura...$(NC)"
	$(DOCKER_COMPOSE_DEV) exec web pytest --cov=apps --cov-report=html

# =============================================================================
# COMANDOS DE CONFIGURAÇÃO
# =============================================================================

setup-env: ## Cria arquivo .env baseado no .env.prod
	@if [ ! -f .env ]; then \
		echo "$(YELLOW)Criando arquivo .env...$(NC)"; \
		cp .env.prod .env; \
		echo "$(GREEN)Arquivo .env criado! Edite-o com suas configurações.$(NC)"; \
	else \
		echo "$(YELLOW)Arquivo .env já existe.$(NC)"; \
	fi

init: ## Inicialização completa do projeto
	@echo "$(GREEN)Inicializando projeto Havoc...$(NC)"
	$(MAKE) setup-env
	$(MAKE) dev-build
	$(MAKE) dev-up
	@echo "$(YELLOW)Aguardando serviços...$(NC)"
	sleep 30
	$(MAKE) dev-migrate
	$(MAKE) dev-collectstatic
	@echo "$(GREEN)Projeto inicializado! Acesse http://localhost:8000$(NC)"
