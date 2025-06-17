# 🚀 COMANDOS MELHORADOS - PROJETO HAVOC

## 📋 **COMANDOS ESSENCIAIS ATUALIZADOS**

### **🎯 Deploy Automático (RECOMENDADO)**

```powershell
# Windows - Deploy completo em um comando
.\deploy_simples.ps1 dev

# Verificar sistema
.\deploy_simples.ps1 check

# Limpar ambiente
.\deploy_simples.ps1 clean

# Gerar nova SECRET_KEY
.\deploy_simples.ps1 secret
```

```bash
# Linux/Mac - Deploy completo em um comando
./deploy_melhorado.sh dev

# Ubuntu - Deploy otimizado (RECOMENDADO)
./deploy_ubuntu.sh dev

# Verificar sistema
./deploy_melhorado.sh check
./deploy_ubuntu.sh check

# Limpar ambiente
./deploy_melhorado.sh clean
./deploy_ubuntu.sh clean
```

---

## 🔧 **SOLUÇÃO DE PROBLEMAS COMUNS**

### **❌ Erro: "SECRET_KEY é obrigatória"**
```powershell
# Windows
.\deploy_simples.ps1 clean
.\deploy_simples.ps1 secret
```

```bash
# Ubuntu/Linux
./deploy_ubuntu.sh clean
./deploy_ubuntu.sh secret
```

### **❌ Erro: "Unable to configure handler 'file'"**
```powershell
# Windows - Limpar variável LOG_FILE
$env:LOG_FILE = $null
.\deploy_simples.ps1 clean
```

### **❌ Erro: "connection to server failed"**
```powershell
# Usar SQLite para desenvolvimento
.\deploy_simples.ps1 dev
```

### **❌ Erro: "DJANGO_SETTINGS_MODULE"**
```powershell
# Windows
$env:DJANGO_SETTINGS_MODULE = "core.settings"
.\deploy_simples.ps1 clean
```

---

## 🧪 **COMANDOS DE TESTE**

### **✅ Verificar se tudo está funcionando:**

```bash
# Verificar sistema
python manage.py check

# Testar URLs principais
curl http://localhost:8000
curl http://localhost:8000/admin/
curl http://localhost:8000/health/

# Verificar logs do servidor
# (executar em terminal separado)
python manage.py runserver
```

---

## 📊 **INFORMAÇÕES DO SISTEMA**

### **🔑 Credenciais Padrão:**
- **URL:** http://localhost:8000
- **Admin:** http://localhost:8000/admin/
- **Usuário:** admin@havoc.com
- **Senha:** admin123

### **📁 Arquivos Importantes:**
- `.env` - Configurações de ambiente
- `db.sqlite3` - Banco de dados SQLite
- `staticfiles/` - Arquivos estáticos coletados
- `media/` - Uploads de usuários

### **🌐 URLs Principais:**
- `/` - Homepage
- `/accounts/login/` - Login
- `/accounts/registro/` - Registro
- `/admin/` - Administração
- `/artigos/` - Blog/Artigos
- `/health/` - Health Check

---

## 🔄 **COMANDOS DE MANUTENÇÃO**

### **🧹 Limpeza:**
```bash
# Limpar cache Python
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +

# Limpar arquivos estáticos
rm -rf staticfiles/*

# Limpar logs
rm -rf logs/*
```

### **🔄 Reset Completo:**
```bash
# Parar servidor (Ctrl+C)

# Limpar banco de dados
rm db.sqlite3

# Limpar migrações (cuidado!)
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

# Recriar migrações
python manage.py makemigrations
python manage.py migrate

# Recriar superusuário
python manage.py createsuperuser
```

---

## 🐳 **COMANDOS DOCKER (PRODUÇÃO)**

### **🚀 Deploy com Docker:**
```bash
# Construir e iniciar
docker-compose up -d

# Verificar status
docker-compose ps

# Ver logs
docker-compose logs -f

# Parar serviços
docker-compose down

# Rebuild completo
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### **🔧 Manutenção Docker:**
```bash
# Executar comandos no container
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic
docker-compose exec web python manage.py createsuperuser

# Backup do banco
docker-compose exec db pg_dump -U havoc_user havoc_prod > backup.sql

# Restaurar backup
docker-compose exec -T db psql -U havoc_user havoc_prod < backup.sql
```

---

## 📝 **COMANDOS DE DESENVOLVIMENTO**

### **🔍 Debug e Logs:**
```bash
# Executar com debug detalhado
python manage.py runserver --verbosity=2

# Shell Django
python manage.py shell

# Executar comando personalizado
python manage.py shell -c "from django.contrib.auth import get_user_model; print(get_user_model().objects.count())"
```

### **📊 Informações do Sistema:**
```bash
# Versão do Django
python manage.py version

# Configurações atuais
python manage.py diffsettings

# Verificar migrações
python manage.py showmigrations

# Criar migrações
python manage.py makemigrations
```

---

## 🎯 **FLUXO RECOMENDADO**

### **🚀 Para Desenvolvimento:**
1. `.\deploy_simples.ps1 dev` (Windows) ou `./deploy_melhorado.sh dev` (Linux)
2. Acessar http://localhost:8000
3. Fazer login no admin com admin@havoc.com / admin123

### **🔧 Para Correção de Problemas:**
1. `.\deploy_simples.ps1 clean`
2. `.\deploy_simples.ps1 check`
3. Se necessário: `.\deploy_simples.ps1 dev`

### **🌐 Para Produção:**
1. Configurar `.env` para produção
2. `docker-compose up -d`
3. Verificar logs: `docker-compose logs -f`

---

**✅ Status:** Todos os comandos testados e funcionais em 17/06/2025
