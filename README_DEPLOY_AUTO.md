# 🤖 DEPLOY TOTALMENTE AUTOMATIZADO - HAVOC

## 🎯 **VISÃO GERAL**

Sistema de deploy **100% automatizado** com configuração interativa que guia você passo a passo na configuração do ambiente, desde a geração de chaves de segurança até a configuração completa do banco de dados e email.

### **✨ Características:**
- 🤖 **Configuração totalmente interativa**
- 🔐 **Geração automática de SECRET_KEY**
- 🌐 **Detecção automática de IP público**
- 📧 **Configuração de email com validação**
- 🗄️ **Suporte a PostgreSQL, MySQL e SQLite**
- ⚙️ **Configuração de Redis opcional**
- 🔒 **Configurações de segurança automáticas**
- 📋 **Resumo e confirmação antes de aplicar**

---

## 🚀 **INÍCIO RÁPIDO**

### **🐧 Linux/Ubuntu:**
```bash
# 1. Tornar executável
chmod +x deploy.sh

# 2. Deploy automatizado (recomendado)
./deploy.sh auto

# 3. Seguir as instruções interativas
# 4. Acessar: http://localhost:8000
```

### **🪟 Windows:**
```powershell
# 1. Deploy automatizado (recomendado)
.\deploy_auto.ps1 auto

# 2. Seguir as instruções interativas
# 3. Acessar: http://localhost:8000
```

**É isso! O sistema fará todo o resto automaticamente!** 🎉

---

## 📋 **PROCESSO INTERATIVO**

### **1. 🔧 Configurações Básicas**
```
🔧 Escolha o tipo de ambiente (1 ou 2) [padrão: 2]: 
   1) Desenvolvimento (debug ativo)
   2) Produção (debug desativo, seguro)

🔐 Gerar nova SECRET_KEY automaticamente? [Y/n]: y
✅ SECRET_KEY gerada automaticamente
```

### **2. 🌐 Configurações de Rede**
```
🔧 Hosts permitidos [padrão: localhost,127.0.0.1,SEU-IP]: 
ℹ️  IP público detectado: 203.0.113.1

🔧 Origens CSRF [padrão: http://localhost:8000,http://SEU-IP:8000]: 
```

### **3. 🗄️ Configurações de Banco**
```
🔧 Escolha o tipo de banco (1, 2 ou 3) [padrão: 1]: 
   1) PostgreSQL (recomendado para produção)
   2) MySQL/MariaDB  
   3) SQLite (apenas para desenvolvimento)

🔧 Nome do banco de dados [padrão: havoc_prod]: 
🔧 Usuário do banco [padrão: havoc_user]: 
🔐 Senha do banco [padrão: ****]: 
```

### **4. 📧 Configurações de Email**
```
❓ Configurar email SMTP? [y/N]: y

🔧 Host SMTP [padrão: smtp.gmail.com]: 
🔧 Porta SMTP [padrão: 587]: 
🔧 Usuário/Email: seu-email@gmail.com
🔐 Senha do email: 
✅ Email configurado: seu-email@gmail.com
```

### **5. ⚙️ Configurações Opcionais**
```
❓ Habilitar Redis para cache? [Y/n]: y
✅ Redis habilitado

❓ Habilitar redirecionamento HTTPS? [y/N]: n
ℹ️  HTTPS desabilitado
```

### **6. 📋 Resumo e Confirmação**
```
=== RESUMO DA CONFIGURAÇÃO ===

ℹ️  Ambiente: production
ℹ️  Debug: False
ℹ️  Banco: postgresql
ℹ️  Nome do banco: havoc_prod
ℹ️  Usuário: havoc_user
ℹ️  Host: db:5432
ℹ️  Hosts permitidos: localhost,127.0.0.1,203.0.113.1
ℹ️  Email backend: django.core.mail.backends.smtp.EmailBackend
ℹ️  Redis: Habilitado
ℹ️  HTTPS: False

❓ Confirma a configuração acima? [Y/n]: y
✅ Configuração salva em .env
```

---

## 🎛️ **COMANDOS DISPONÍVEIS**

### **🤖 Automatizado (Recomendado):**
```bash
# Linux
./deploy.sh auto          # Deploy completo automatizado
./deploy.sh config        # Apenas configuração interativa

# Windows  
.\deploy_auto.ps1 auto    # Deploy completo automatizado
.\deploy_auto.ps1 config  # Apenas configuração interativa
```

### **🔧 Manual:**
```bash
# Linux
./deploy.sh deploy        # Deploy tradicional
./deploy.sh build         # Apenas build
./deploy.sh quick         # Deploy rápido

# Windows
.\deploy_auto.ps1 deploy  # Deploy tradicional  
.\deploy_auto.ps1 build   # Apenas build
```

### **📊 Gerenciamento:**
```bash
# Ambos os sistemas
docker-compose logs -f    # Ver logs
docker-compose down       # Parar
docker-compose ps         # Status
```

---

## 🔍 **DETALHES DO PROCESSO AUTOMATIZADO**

### **1. 🔍 Verificação de Dependências**
- ✅ Verifica se Docker está instalado
- ✅ Verifica se Docker Compose está disponível
- ✅ Valida arquivos necessários do projeto

### **2. 🤖 Configuração Inteligente**
- 🌐 **Detecção automática** do IP público
- 🔐 **Geração segura** de SECRET_KEY
- 📧 **Validação** de endereços de email
- 🗄️ **Configuração otimizada** por tipo de banco
- ⚙️ **Sugestões inteligentes** baseadas no ambiente

### **3. 📁 Criação do Arquivo .env**
- 📝 **Backup automático** do .env anterior
- 🏷️ **Comentários explicativos** em cada seção
- 📅 **Timestamp** de criação
- ✅ **Validação** de todas as configurações

### **4. 🐳 Build e Deploy**
- 🏗️ **Build** da imagem Docker
- 🚀 **Inicialização** dos serviços
- 🏥 **Health checks** automáticos
- 📊 **Verificação** de conectividade

### **5. ✅ Validação Final**
- 🌐 **Teste** de endpoints principais
- 📋 **Relatório** de status dos serviços
- 📝 **Informações** de acesso
- 🔧 **Comandos úteis** para gerenciamento

---

## 🔧 **CONFIGURAÇÕES GERADAS**

### **📄 Arquivo .env Criado:**
```env
# =============================================================================
# CONFIGURAÇÕES DO HAVOC - GERADO AUTOMATICAMENTE
# Gerado em: 2025-06-16 15:30:45
# =============================================================================

# Ambiente
ENVIRONMENT=production
DEBUG=False

# Segurança
SECRET_KEY=django-insecure-a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0
ALLOWED_HOSTS=localhost,127.0.0.1,203.0.113.1
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://203.0.113.1:8000

# Banco de dados
DATABASE_ENGINE=postgresql
DB_NAME=havoc_prod
DB_USER=havoc_user
DB_PASSWORD=Xy9#mK2$vN8@
DB_HOST=db
DB_PORT=5432

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-app
DEFAULT_FROM_EMAIL=seu-email@gmail.com

# Cache
REDIS_URL=redis://redis:6379/1

# HTTPS
SECURE_SSL_REDIRECT=False

# ... outras configurações automáticas
```

---

## 🎯 **CENÁRIOS DE USO**

### **🧪 Desenvolvimento Local:**
```bash
# Configuração rápida para desenvolvimento
./deploy.sh auto

# Escolher:
# - Ambiente: Desenvolvimento (1)
# - Banco: SQLite (3) 
# - Email: Console (n)
# - Redis: Não (n)
```

### **🌐 Servidor de Teste:**
```bash
# Configuração para servidor de teste
./deploy.sh auto

# Escolher:
# - Ambiente: Produção (2)
# - Banco: PostgreSQL (1)
# - Email: SMTP (y)
# - Redis: Sim (y)
# - HTTPS: Não (n)
```

### **🚀 Produção:**
```bash
# Configuração para produção
./deploy.sh auto

# Escolher:
# - Ambiente: Produção (2)
# - Banco: PostgreSQL (1)
# - Email: SMTP (y) 
# - Redis: Sim (y)
# - HTTPS: Sim (y)
```

---

## 🔒 **SEGURANÇA AUTOMÁTICA**

### **🔐 Geração de Chaves:**
- **SECRET_KEY:** Gerada automaticamente com 50 caracteres
- **DB_PASSWORD:** Gerada automaticamente se não especificada
- **Backup:** .env anterior sempre preservado

### **🛡️ Configurações de Produção:**
- **DEBUG=False** em produção
- **Cookies seguros** habilitados
- **CSRF protection** configurado
- **HTTPS redirect** opcional
- **Headers de segurança** configurados

### **📧 Validação de Email:**
- **Formato** validado automaticamente
- **Fallback** para console se inválido
- **Configuração SMTP** testada

---

## 🎉 **RESULTADO FINAL**

### **🌐 URLs Disponíveis:**
- **Aplicação:** http://localhost:8000
- **Admin:** http://localhost:8000/admin/ (admin/admin123)
- **Health Check:** http://localhost:8000/health/
- **Config:** http://localhost:8000/config/

### **📊 Serviços Ativos:**
- ✅ **Django** (aplicação principal)
- ✅ **PostgreSQL** (banco de dados)
- ✅ **Nginx** (proxy reverso)
- ✅ **Redis** (cache - se habilitado)

### **🔧 Comandos Úteis:**
```bash
# Ver logs em tempo real
docker-compose logs -f

# Status dos serviços
docker-compose ps

# Parar tudo
docker-compose down

# Reiniciar
docker-compose restart
```

---

## 🆘 **TROUBLESHOOTING**

### **❌ Erro: Docker não encontrado**
```bash
# Ubuntu/Linux
sudo apt install docker.io docker-compose

# Windows
# Instalar Docker Desktop
```

### **❌ Erro: Permissão negada**
```bash
# Linux - adicionar usuário ao grupo docker
sudo usermod -aG docker $USER
newgrp docker
```

### **❌ Erro: Porta 8000 ocupada**
```bash
# Verificar o que está usando a porta
sudo netstat -tulpn | grep :8000

# Parar processo
sudo kill -9 PID
```

### **❌ Erro: Banco não conecta**
```bash
# Verificar logs do banco
docker-compose logs db

# Reiniciar banco
docker-compose restart db
```

---

## 📚 **DOCUMENTAÇÃO ADICIONAL**

- 📖 **[DEPLOY_UBUNTU.md](DEPLOY_UBUNTU.md)** - Guia completo Ubuntu
- ⚡ **[COMANDOS_RAPIDOS.md](COMANDOS_RAPIDOS.md)** - Comandos úteis
- 🔧 **[README_DEPLOY.md](README_DEPLOY.md)** - Deploy manual
- 🧪 **[test_deploy.ps1](test_deploy.ps1)** - Testes Windows

---

**🎯 O deploy automatizado torna o processo simples, seguro e confiável!**

**Basta executar um comando e seguir as instruções interativas!** 🚀
