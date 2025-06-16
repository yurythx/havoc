# 🐳 DEPLOY HAVOC EM CONTAINER - README

## 📋 **VISÃO GERAL**

Este projeto inclui uma configuração completa para deploy em container Docker, permitindo executar o sistema Havoc em qualquer ambiente que suporte Docker.

### **🎯 Características:**
- ✅ **Deploy automatizado** com scripts
- ✅ **PostgreSQL** como banco de dados
- ✅ **Nginx** como proxy reverso
- ✅ **Redis** para cache (opcional)
- ✅ **Backup automático** configurado
- ✅ **SSL/HTTPS** pronto para configurar
- ✅ **Monitoramento** integrado

---

## 🚀 **INÍCIO RÁPIDO**

### **Para Ubuntu/Debian:**
```bash
# 1. Instalar dependências
chmod +x install_ubuntu.sh
./install_ubuntu.sh

# 2. Configurar ambiente
cp .env.docker .env
nano .env  # Editar configurações

# 3. Deploy
chmod +x deploy.sh
./deploy.sh deploy

# 4. Acessar
# http://seu-ip:8000
```

### **Para outros sistemas:**
1. Instale Docker e Docker Compose
2. Configure o arquivo `.env`
3. Execute `./deploy.sh deploy`

---

## 📁 **ESTRUTURA DE ARQUIVOS**

```
havoc/
├── 📄 Dockerfile                 # Imagem Docker da aplicação
├── 📄 docker-compose.yml         # Orquestração dos serviços
├── 📄 .env.docker                # Configurações de exemplo
├── 📄 deploy.sh                  # Script de deploy
├── 📄 install_ubuntu.sh          # Instalação automática Ubuntu
├── 📁 docker/                    # Configurações Docker
│   ├── 📄 entrypoint.sh          # Script de inicialização
│   ├── 📄 start.sh               # Script de start
│   ├── 📁 nginx/                 # Configuração Nginx
│   └── 📁 postgres/              # Configuração PostgreSQL
├── 📄 requirements.txt           # Dependências Python
├── 📄 requirements-prod.txt      # Dependências de produção
└── 📁 core/
    └── 📄 settings_prod.py       # Configurações de produção
```

---

## ⚙️ **CONFIGURAÇÃO**

### **1. Arquivo .env**
Copie `.env.docker` para `.env` e configure:

```bash
# Segurança (OBRIGATÓRIO alterar)
SECRET_KEY=sua-chave-secreta-unica

# Banco de dados
DB_PASSWORD=senha-segura-do-banco

# Hosts permitidos
ALLOWED_HOSTS=localhost,seu-ip,seu-dominio.com

# Email (opcional)
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-app
```

### **2. Gerar SECRET_KEY**
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print('SECRET_KEY=' + get_random_secret_key())"
```

---

## 🔧 **COMANDOS DISPONÍVEIS**

### **Script de Deploy:**
```bash
./deploy.sh deploy    # Deploy completo
./deploy.sh quick     # Deploy rápido
./deploy.sh logs      # Ver logs
./deploy.sh stop      # Parar aplicação
./deploy.sh clean     # Limpar tudo
./deploy.sh secret    # Gerar SECRET_KEY
```

### **Docker Compose:**
```bash
docker-compose up -d        # Iniciar
docker-compose down         # Parar
docker-compose ps           # Status
docker-compose logs web     # Logs específicos
docker-compose restart web  # Reiniciar serviço
```

### **Django:**
```bash
# Shell Django
docker-compose exec web python manage.py shell

# Criar superusuário
docker-compose exec web python manage.py createsuperuser

# Migrações
docker-compose exec web python manage.py migrate

# Coletar estáticos
docker-compose exec web python manage.py collectstatic
```

---

## 🏗️ **SERVIÇOS INCLUÍDOS**

### **1. Web (Django)**
- **Porta:** 8000
- **Imagem:** Construída localmente
- **Função:** Aplicação principal

### **2. Database (PostgreSQL)**
- **Porta:** 5432
- **Imagem:** postgres:15-alpine
- **Função:** Banco de dados principal

### **3. Nginx (Proxy Reverso)**
- **Portas:** 80, 443
- **Imagem:** nginx:alpine
- **Função:** Servidor web e proxy

### **4. Redis (Cache) - Opcional**
- **Porta:** 6379
- **Imagem:** redis:7-alpine
- **Função:** Cache e sessões

---

## 💾 **BACKUP E RESTORE**

### **Backup Automático:**
```bash
# Backup do banco
docker-compose exec db pg_dump -U havoc_user havoc_prod > backup.sql

# Backup completo
tar -czf backup_completo.tar.gz backup.sql media/ logs/ .env
```

### **Restore:**
```bash
# Restore do banco
docker-compose exec -T db psql -U havoc_user havoc_prod < backup.sql
```

### **Backup Automático (Cron):**
```bash
# Adicionar ao crontab para backup diário às 2h
0 2 * * * cd /caminho/havoc && docker-compose exec db pg_dump -U havoc_user havoc_prod > backup_$(date +\%Y\%m\%d).sql
```

---

## 🌐 **CONFIGURAÇÃO DE DOMÍNIO**

### **1. DNS:**
Configure seu domínio para apontar para o IP do servidor:
```
A    @              IP-DO-SERVIDOR
A    www            IP-DO-SERVIDOR
```

### **2. Nginx:**
Edite `docker/nginx/default.conf`:
```nginx
server_name seu-dominio.com www.seu-dominio.com;
```

### **3. SSL (Let's Encrypt):**
```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx

# Obter certificado
sudo certbot --nginx -d seu-dominio.com -d www.seu-dominio.com
```

---

## 🔍 **MONITORAMENTO**

### **Logs:**
```bash
# Logs em tempo real
docker-compose logs -f

# Logs específicos
docker-compose logs web
docker-compose logs db
docker-compose logs nginx
```

### **Recursos:**
```bash
# Status dos containers
docker-compose ps

# Uso de recursos
docker stats

# Espaço em disco
df -h
```

### **Health Checks:**
```bash
# Verificar aplicação
curl -f http://localhost:8000

# Verificar banco
docker-compose exec db pg_isready -U havoc_user
```

---

## 🔒 **SEGURANÇA**

### **Firewall (Ubuntu):**
```bash
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 8000
sudo ufw enable
```

### **Configurações de Segurança:**
- ✅ **SECRET_KEY** única
- ✅ **DEBUG=False** em produção
- ✅ **ALLOWED_HOSTS** configurado
- ✅ **CSRF_TRUSTED_ORIGINS** configurado
- ✅ **HTTPS** recomendado para produção

---

## 🚨 **TROUBLESHOOTING**

### **Problemas Comuns:**

#### **Container não inicia:**
```bash
docker-compose logs NOME_CONTAINER
docker-compose restart NOME_CONTAINER
```

#### **Porta ocupada:**
```bash
sudo netstat -tulpn | grep :8000
sudo kill -9 PID
```

#### **Sem espaço em disco:**
```bash
docker system prune -f
sudo apt autoremove -y
```

#### **Banco não conecta:**
```bash
docker-compose restart db
docker-compose logs db
```

#### **Reset completo:**
```bash
# CUIDADO: Apaga todos os dados
docker-compose down -v
docker system prune -a -f
./deploy.sh deploy
```

---

## 📊 **REQUISITOS DO SISTEMA**

### **Mínimo:**
- **OS:** Ubuntu 20.04+ (ou qualquer Linux com Docker)
- **RAM:** 2GB
- **Disco:** 10GB
- **CPU:** 1 core

### **Recomendado:**
- **OS:** Ubuntu 22.04 LTS
- **RAM:** 4GB+
- **Disco:** 20GB+
- **CPU:** 2+ cores

---

## 🔗 **LINKS ÚTEIS**

### **Acesso à Aplicação:**
- **Principal:** http://seu-ip:8000
- **Admin:** http://seu-ip:8000/admin/
- **Config:** http://seu-ip:8000/config/

### **Credenciais Padrão:**
- **Usuário:** admin
- **Senha:** admin123
- **⚠️ Altere após primeiro login!**

---

## 📚 **DOCUMENTAÇÃO ADICIONAL**

- 📖 **[DEPLOY_UBUNTU.md](DEPLOY_UBUNTU.md)** - Guia completo para Ubuntu
- ⚡ **[COMANDOS_RAPIDOS.md](COMANDOS_RAPIDOS.md)** - Comandos úteis
- 🔧 **[requirements-prod.txt](requirements-prod.txt)** - Dependências de produção

---

## 🆘 **SUPORTE**

### **Logs Importantes:**
```bash
# Logs da aplicação
docker-compose logs web

# Logs do banco
docker-compose logs db

# Logs do sistema
journalctl -f -u docker
```

### **Verificação Rápida:**
```bash
# Status geral
docker-compose ps

# Teste de conectividade
curl -I http://localhost:8000

# Recursos do sistema
free -h && df -h
```

---

**🎉 Parabéns! Seu projeto Havoc está pronto para produção em container!**

Para mais informações, consulte a documentação específica ou os logs do sistema.
