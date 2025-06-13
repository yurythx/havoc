# 🐳 Havoc - Deploy com Docker

Este guia explica como fazer deploy do projeto Havoc usando Docker e Docker Compose.

## 📋 Pré-requisitos

- Docker 20.10+
- Docker Compose 2.0+
- Make (opcional, mas recomendado)

## 🚀 Quick Start

### 1. Configuração Inicial

```bash
# Clone o repositório
git clone <repository-url>
cd havoc

# Configure as variáveis de ambiente
make setup-env
# ou
cp .env.prod .env

# Edite o arquivo .env com suas configurações
nano .env
```

### 2. Desenvolvimento

```bash
# Inicialização completa para desenvolvimento
make init

# Ou manualmente:
make dev-build
make dev-up
make dev-migrate
make dev-collectstatic
```

Acesse: http://localhost:8000

### 3. Produção

```bash
# Deploy completo
make deploy

# Ou manualmente:
make build
make up
make migrate
make collectstatic
```

## 🏗️ Arquitetura

### Serviços

- **web**: Aplicação Django com Gunicorn
- **db**: PostgreSQL 15
- **redis**: Redis para cache e Celery
- **celery_worker**: Worker do Celery
- **celery_beat**: Agendador do Celery
- **flower**: Monitoramento do Celery
- **nginx**: Proxy reverso (produção)

### Volumes

- **postgres_data**: Dados do PostgreSQL
- **redis_data**: Dados do Redis
- **static_volume**: Arquivos estáticos
- **media_volume**: Arquivos de mídia
- **logs_volume**: Logs da aplicação

## 🔧 Comandos Úteis

### Desenvolvimento

```bash
make dev-up          # Iniciar serviços
make dev-down        # Parar serviços
make dev-logs        # Ver logs
make dev-shell       # Shell do container
make dev-migrate     # Executar migrações
make dev-test        # Executar testes
```

### Produção

```bash
make up              # Iniciar serviços
make down            # Parar serviços
make logs            # Ver logs
make shell           # Shell do container
make migrate         # Executar migrações
make restart         # Reiniciar serviços
```

### Manutenção

```bash
make status          # Status dos serviços
make health          # Verificar saúde
make backup-db       # Backup do banco
make clean           # Limpar recursos
```

## 🔐 Configurações de Segurança

### Variáveis Obrigatórias

```env
SECRET_KEY=sua-chave-secreta-muito-forte
DB_PASSWORD=senha-forte-do-banco
ALLOWED_HOSTS=seu-dominio.com
CSRF_TRUSTED_ORIGINS=https://seu-dominio.com
```

### HTTPS em Produção

1. Obtenha certificados SSL
2. Coloque em `docker/nginx/ssl/`
3. Descomente configuração HTTPS no nginx
4. Configure `SECURE_SSL_REDIRECT=True`

## 📊 Monitoramento

### Health Checks

- **Web**: http://localhost:8000/health/
- **Flower**: http://localhost:5555/
- **Nginx**: http://localhost/health/

### Logs

```bash
# Logs em tempo real
make logs

# Logs específicos
docker-compose logs web
docker-compose logs celery_worker
```

### Métricas

```bash
# Estatísticas dos containers
make monitor

# Processos dos containers
make top
```

## 🔄 Deploy e Atualizações

### Deploy Inicial

```bash
# 1. Configure ambiente
make setup-env

# 2. Deploy completo
make deploy

# 3. Crie superusuário
make createsuperuser
```

### Atualizações

```bash
# Deploy rápido (sem rebuild)
make quick-deploy

# Deploy completo (com rebuild)
make deploy
```

### Rollback

```bash
# Parar serviços
make down

# Restaurar backup
make restore-db FILE=backup_20231201_120000.sql

# Reiniciar
make up
```

## 🗄️ Backup e Restore

### Backup Automático

```bash
# Backup manual
make backup-db

# Backup agendado (adicione ao cron)
0 2 * * * cd /path/to/havoc && make backup-db
```

### Restore

```bash
make restore-db FILE=backup_20231201_120000.sql
```

## 🐛 Troubleshooting

### Problemas Comuns

1. **Serviços não iniciam**
   ```bash
   make logs
   # Verifique logs para erros
   ```

2. **Banco não conecta**
   ```bash
   # Verifique se PostgreSQL está rodando
   docker-compose ps db
   
   # Teste conexão
   docker-compose exec db pg_isready -U postgres
   ```

3. **Arquivos estáticos não carregam**
   ```bash
   make collectstatic
   make restart-web
   ```

4. **Celery não processa tarefas**
   ```bash
   # Verifique worker
   docker-compose logs celery_worker
   
   # Reinicie Celery
   make restart-celery
   ```

### Debug

```bash
# Shell do Django
make django-shell

# Shell do container
make shell

# Logs detalhados
docker-compose logs -f --tail=100 web
```

## 📈 Performance

### Configurações Recomendadas

#### Produção Pequena (1-2 GB RAM)
```env
GUNICORN_WORKERS=2
CELERY_WORKER_CONCURRENCY=2
```

#### Produção Média (4-8 GB RAM)
```env
GUNICORN_WORKERS=4
CELERY_WORKER_CONCURRENCY=4
```

#### Produção Grande (8+ GB RAM)
```env
GUNICORN_WORKERS=8
CELERY_WORKER_CONCURRENCY=8
```

### Otimizações

1. **Redis**: Configure maxmemory apropriada
2. **PostgreSQL**: Ajuste shared_buffers e effective_cache_size
3. **Nginx**: Configure cache para arquivos estáticos
4. **Gunicorn**: Use worker_class=gevent para I/O intensivo

## 🔒 Segurança

### Checklist de Segurança

- [ ] SECRET_KEY única e forte
- [ ] Senhas de banco fortes
- [ ] HTTPS configurado
- [ ] Firewall configurado
- [ ] Backups regulares
- [ ] Logs monitorados
- [ ] Atualizações regulares

### Hardening

1. **Usuário não-root**: Containers rodam como usuário django
2. **Volumes**: Dados persistentes em volumes Docker
3. **Networks**: Isolamento de rede entre serviços
4. **Secrets**: Use Docker secrets para dados sensíveis

## 📞 Suporte

Para problemas ou dúvidas:

1. Verifique logs: `make logs`
2. Consulte documentação
3. Abra issue no repositório

## 📝 Changelog

### v1.0.0
- Setup inicial do Docker
- Configuração de produção
- Scripts de deploy
- Monitoramento básico
