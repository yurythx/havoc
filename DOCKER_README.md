# 🐳 HAVOC - Deploy com Docker

## 🚀 **Deploy Rápido**

### **Pré-requisitos**
- Docker 20.10+
- Docker Compose 2.0+

### **Comandos Básicos**
```bash
# 1. Configurar ambiente
cp .env.prod .env
# Editar .env com suas configurações

# 2. Deploy
docker-compose build
docker-compose up -d

# 3. Verificar
docker-compose logs -f
```

---

## ⚙️ **Configuração**

### **Arquivo .env (obrigatório)**
```bash
# Copiar template
cp .env.prod .env

# Configurações mínimas necessárias
SECRET_KEY=sua-chave-secreta-unica-aqui
ALLOWED_HOSTS=seu-dominio.com,localhost
DB_PASSWORD=senha-segura-do-banco
```

### **Configurações Importantes**
```bash
# Produção
DEBUG=False
ENVIRONMENT=production
ALLOWED_HOSTS=meudominio.com,www.meudominio.com

# Banco de dados
DB_NAME=havoc_prod
DB_USER=postgres
DB_PASSWORD=senha-muito-segura

# Email (opcional)
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-de-app
```

---

## 🛠️ **Comandos Úteis**

### **Gerenciamento**
```bash
# Ver logs
docker-compose logs -f

# Status dos serviços
docker-compose ps

# Reiniciar serviços
docker-compose restart

# Parar tudo
docker-compose down
```

### **Manutenção**
```bash
# Backup do banco
docker-compose exec db pg_dump -U postgres havoc_prod > backup.sql

# Restaurar backup
docker-compose exec -T db psql -U postgres havoc_prod < backup.sql

# Shell do Django
docker-compose exec web python manage.py shell

# Criar superusuário
docker-compose exec web python manage.py createsuperuser
```

### **Com Makefile**
```bash
# Deploy completo
make deploy

# Comandos úteis
make logs
make status
make health
make backup-db
```

---

## 🏗️ **Estrutura dos Serviços**

### **Serviços Incluídos**
- **web** - Aplicação Django (Gunicorn)
- **db** - PostgreSQL 15
- **nginx** - Proxy reverso (opcional)

### **Portas**
- **8000** - Aplicação Django
- **80** - Nginx (se habilitado)
- **5432** - PostgreSQL (para debug)

### **Volumes**
- **postgres_data** - Dados do banco
- **static_volume** - Arquivos estáticos
- **media_volume** - Uploads
- **logs_volume** - Logs

---

## 🔧 **Personalização**

### **Variáveis de Ambiente Disponíveis**
```bash
# Django
SECRET_KEY=
DEBUG=False
ALLOWED_HOSTS=
CSRF_TRUSTED_ORIGINS=

# Banco
DB_NAME=havoc_prod
DB_USER=postgres
DB_PASSWORD=
DB_HOST=db
DB_PORT=5432

# Gunicorn
GUNICORN_WORKERS=4
GUNICORN_TIMEOUT=30

# Email
EMAIL_HOST=
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=

# Site
SITE_NAME=Havoc
SITE_URL=https://meudominio.com
```

---

## 🚨 **Troubleshooting**

### **Problemas Comuns**

**1. Erro de conexão com banco**
```bash
# Verificar se o banco está rodando
docker-compose ps db

# Ver logs do banco
docker-compose logs db
```

**2. Erro 500 na aplicação**
```bash
# Ver logs da aplicação
docker-compose logs web

# Verificar configurações
docker-compose exec web python manage.py check
```

**3. Arquivos estáticos não carregam**
```bash
# Coletar arquivos estáticos
docker-compose exec web python manage.py collectstatic --noinput
```

**4. Problemas de permissão**
```bash
# Verificar permissões dos volumes
docker-compose exec web ls -la /app/
```

### **Reset Completo**
```bash
# ATENÇÃO: Remove todos os dados!
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

---

## 🔒 **Segurança**

### **Checklist de Segurança**
- ✅ SECRET_KEY única e forte
- ✅ DEBUG=False em produção
- ✅ Senhas do banco fortes
- ✅ ALLOWED_HOSTS configurado
- ✅ HTTPS configurado (recomendado)

### **Configuração HTTPS**
```bash
# No .env
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

---

## 📈 **Performance**

### **Otimizações**
```bash
# Mais workers Gunicorn
GUNICORN_WORKERS=8

# Cache Redis (opcional)
REDIS_URL=redis://redis:6379/0

# Configurações de banco
DB_CONN_MAX_AGE=60
```

### **Monitoramento**
```bash
# Estatísticas dos containers
docker stats

# Health checks
curl http://localhost:8000/health/
```

---

## 🌐 **Deploy em Cloud**

### **AWS ECS**
- Usar task definition baseada no docker-compose.yml
- Configurar ALB para load balancing
- RDS para PostgreSQL

### **Google Cloud Run**
- Build da imagem: `docker build -t gcr.io/PROJECT/havoc .`
- Deploy: `gcloud run deploy --image gcr.io/PROJECT/havoc`

### **DigitalOcean**
- App Platform suporta docker-compose.yml
- Configurar variáveis de ambiente no painel

---

## 📞 **Suporte**

### **Logs Importantes**
```bash
# Logs da aplicação
docker-compose logs web

# Logs do banco
docker-compose logs db

# Logs do nginx
docker-compose logs nginx
```

### **Comandos de Debug**
```bash
# Shell do container
docker-compose exec web bash

# Verificar configurações Django
docker-compose exec web python manage.py check --deploy

# Testar conexão com banco
docker-compose exec web python manage.py dbshell
```

---

## ✅ **Checklist de Deploy**

### **Antes do Deploy**
- [ ] Docker e Docker Compose instalados
- [ ] Arquivo .env configurado
- [ ] SECRET_KEY gerada
- [ ] ALLOWED_HOSTS configurado
- [ ] Senhas do banco definidas

### **Após o Deploy**
- [ ] Aplicação acessível
- [ ] Health check funcionando
- [ ] Admin acessível (/admin/)
- [ ] Arquivos estáticos carregando
- [ ] Backup configurado

---

**🎉 Projeto Havoc pronto para produção com Docker!**
