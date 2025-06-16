# 🐧 DEPLOY HAVOC EM UBUNTU - GUIA COMPLETO

## 📋 **ÍNDICE**
1. [Pré-requisitos](#pré-requisitos)
2. [Instalação do Docker](#instalação-do-docker)
3. [Preparação do Projeto](#preparação-do-projeto)
4. [Configuração](#configuração)
5. [Deploy](#deploy)
6. [Verificação](#verificação)
7. [Comandos Úteis](#comandos-úteis)
8. [Troubleshooting](#troubleshooting)

---

## 🔧 **PRÉ-REQUISITOS**

### **Sistema Operacional:**
- Ubuntu 20.04 LTS ou superior
- Mínimo 2GB RAM
- Mínimo 10GB espaço em disco
- Acesso root ou sudo

### **Verificar Sistema:**
```bash
# Verificar versão do Ubuntu
lsb_release -a

# Verificar recursos
free -h
df -h

# Atualizar sistema
sudo apt update && sudo apt upgrade -y
```

---

## 🐳 **INSTALAÇÃO DO DOCKER**

### **1. Remover versões antigas (se existirem):**
```bash
sudo apt remove docker docker-engine docker.io containerd runc
```

### **2. Instalar dependências:**
```bash
sudo apt update
sudo apt install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    git \
    unzip
```

### **3. Adicionar chave GPG oficial do Docker:**
```bash
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
```

### **4. Adicionar repositório do Docker:**
```bash
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

### **5. Instalar Docker Engine:**
```bash
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

### **6. Instalar Docker Compose (versão standalone):**
```bash
# Baixar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Dar permissão de execução
sudo chmod +x /usr/local/bin/docker-compose

# Criar link simbólico
sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
```

### **7. Configurar usuário para usar Docker sem sudo:**
```bash
# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER

# Aplicar mudanças (ou fazer logout/login)
newgrp docker
```

### **8. Verificar instalação:**
```bash
# Verificar Docker
docker --version
docker run hello-world

# Verificar Docker Compose
docker-compose --version
```

---

## 📁 **PREPARAÇÃO DO PROJETO**

### **1. Clonar ou transferir projeto:**

#### **Opção A: Via Git (se o projeto estiver em repositório):**
```bash
# Clonar repositório
git clone https://github.com/seu-usuario/havoc.git
cd havoc
```

#### **Opção B: Transferir arquivos via SCP:**
```bash
# Do seu computador local para o servidor Ubuntu
scp -r /caminho/para/havoc usuario@ip-servidor:/home/usuario/

# No servidor
cd /home/usuario/havoc
```

#### **Opção C: Upload via FTP/SFTP:**
Use um cliente como FileZilla ou WinSCP para transferir os arquivos.

### **2. Verificar estrutura do projeto:**
```bash
ls -la

# Deve conter:
# - Dockerfile
# - docker-compose.yml
# - requirements.txt
# - manage.py
# - apps/
# - core/
# - .env.docker
```

---

## ⚙️ **CONFIGURAÇÃO**

### **1. Configurar arquivo de ambiente:**
```bash
# Copiar arquivo de exemplo
cp .env.docker .env

# Editar configurações
nano .env
```

### **2. Configurações importantes no .env:**
```bash
# SEGURANÇA - GERAR NOVA SECRET_KEY
SECRET_KEY=sua-chave-secreta-unica-aqui

# BANCO DE DADOS
DB_PASSWORD=senha-segura-do-banco

# HOSTS PERMITIDOS (adicionar IP/domínio do servidor)
ALLOWED_HOSTS=localhost,127.0.0.1,SEU-IP-SERVIDOR,seu-dominio.com

# CSRF (adicionar domínio)
CSRF_TRUSTED_ORIGINS=http://SEU-IP-SERVIDOR:8000,https://seu-dominio.com

# EMAIL (configurar se necessário)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-app
```

### **3. Gerar SECRET_KEY segura:**
```bash
# Instalar Python se não estiver instalado
sudo apt install python3 python3-pip

# Gerar SECRET_KEY
python3 -c "from django.core.management.utils import get_random_secret_key; print('SECRET_KEY=' + get_random_secret_key())"

# Copiar a saída e colar no arquivo .env
```

### **4. Criar diretórios necessários:**
```bash
mkdir -p logs media staticfiles backups
chmod 755 logs media staticfiles backups
```

---

## 🚀 **DEPLOY**

### **1. Tornar script executável:**
```bash
chmod +x deploy.sh
```

### **2. Executar deploy completo:**
```bash
# Deploy completo (primeira vez)
./deploy.sh deploy
```

### **3. Acompanhar processo:**
O script irá:
- ✅ Verificar dependências
- ✅ Construir imagem Docker
- ✅ Iniciar banco de dados PostgreSQL
- ✅ Executar migrações
- ✅ Coletar arquivos estáticos
- ✅ Criar superusuário padrão
- ✅ Iniciar aplicação

### **4. Aguardar conclusão:**
```bash
# O processo pode levar alguns minutos
# Aguarde a mensagem: "🎉 DEPLOY CONCLUÍDO!"
```

---

## ✅ **VERIFICAÇÃO**

### **1. Verificar containers:**
```bash
# Ver status dos containers
docker-compose ps

# Deve mostrar:
# - havoc_db (PostgreSQL) - Up
# - havoc_web (Django) - Up
# - havoc_nginx (Nginx) - Up
```

### **2. Verificar logs:**
```bash
# Ver logs de todos os serviços
docker-compose logs

# Ver logs específicos
docker-compose logs web
docker-compose logs db
```

### **3. Testar aplicação:**
```bash
# Testar conectividade
curl http://localhost:8000

# Ou abrir no navegador
# http://SEU-IP-SERVIDOR:8000
```

### **4. Acessar admin:**
```bash
# URL: http://SEU-IP-SERVIDOR:8000/admin/
# Usuário: admin
# Senha: admin123
```

---

## 🔧 **COMANDOS ÚTEIS**

### **Gerenciamento de Containers:**
```bash
# Ver logs em tempo real
./deploy.sh logs

# Parar aplicação
./deploy.sh stop

# Reiniciar aplicação
docker-compose restart

# Deploy rápido (sem rebuild)
./deploy.sh quick

# Limpar tudo
./deploy.sh clean
```

### **Comandos Django:**
```bash
# Shell Django
docker-compose exec web python manage.py shell

# Criar superusuário
docker-compose exec web python manage.py createsuperuser

# Executar migrações
docker-compose exec web python manage.py migrate

# Coletar estáticos
docker-compose exec web python manage.py collectstatic
```

### **Backup e Restore:**
```bash
# Backup do banco
docker-compose exec db pg_dump -U havoc_user havoc_prod > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore do banco
docker-compose exec -T db psql -U havoc_user havoc_prod < backup.sql

# Backup completo (arquivos + banco)
tar -czf backup_completo_$(date +%Y%m%d_%H%M%S).tar.gz \
    backup_*.sql media/ logs/ .env
```

---

## 🔥 **TROUBLESHOOTING**

### **Problema: Containers não iniciam**
```bash
# Verificar logs
docker-compose logs

# Verificar espaço em disco
df -h

# Verificar memória
free -h

# Reconstruir imagens
docker-compose build --no-cache
```

### **Problema: Erro de permissão**
```bash
# Verificar se usuário está no grupo docker
groups $USER

# Se não estiver, adicionar
sudo usermod -aG docker $USER
newgrp docker
```

### **Problema: Porta 8000 ocupada**
```bash
# Verificar o que está usando a porta
sudo netstat -tulpn | grep :8000

# Matar processo se necessário
sudo kill -9 PID

# Ou alterar porta no docker-compose.yml
```

### **Problema: Banco de dados não conecta**
```bash
# Verificar se PostgreSQL está rodando
docker-compose ps db

# Verificar logs do banco
docker-compose logs db

# Resetar banco (CUIDADO: apaga dados)
docker-compose down -v
docker-compose up -d
```

### **Problema: Arquivos estáticos não carregam**
```bash
# Coletar estáticos novamente
docker-compose exec web python manage.py collectstatic --clear

# Verificar permissões
docker-compose exec web ls -la /app/staticfiles/
```

---

## 🌐 **CONFIGURAÇÃO DE DOMÍNIO (OPCIONAL)**

### **1. Configurar DNS:**
- Aponte seu domínio para o IP do servidor
- Configure registro A: `seu-dominio.com` → `IP-DO-SERVIDOR`

### **2. Configurar Nginx para domínio:**
```bash
# Editar configuração do Nginx
nano docker/nginx/default.conf

# Alterar server_name
server_name seu-dominio.com www.seu-dominio.com;
```

### **3. Configurar HTTPS com Let's Encrypt:**
```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx

# Obter certificado
sudo certbot --nginx -d seu-dominio.com -d www.seu-dominio.com

# Configurar renovação automática
sudo crontab -e
# Adicionar linha:
# 0 12 * * * /usr/bin/certbot renew --quiet
```

---

## 📊 **MONITORAMENTO**

### **1. Verificar recursos:**
```bash
# CPU e memória
htop

# Espaço em disco
df -h

# Logs do sistema
journalctl -f
```

### **2. Monitorar containers:**
```bash
# Estatísticas em tempo real
docker stats

# Verificar saúde
docker-compose ps
```

---

## 🔒 **SEGURANÇA**

### **1. Firewall:**
```bash
# Instalar UFW
sudo apt install ufw

# Configurar regras básicas
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 8000

# Ativar firewall
sudo ufw enable
```

### **2. Atualizações automáticas:**
```bash
# Instalar unattended-upgrades
sudo apt install unattended-upgrades

# Configurar
sudo dpkg-reconfigure -plow unattended-upgrades
```

---

## 🎯 **CHECKLIST FINAL**

- [ ] Docker e Docker Compose instalados
- [ ] Projeto transferido para servidor
- [ ] Arquivo .env configurado
- [ ] SECRET_KEY gerada
- [ ] ALLOWED_HOSTS configurado
- [ ] Deploy executado com sucesso
- [ ] Aplicação acessível via navegador
- [ ] Admin Django funcionando
- [ ] Backup configurado
- [ ] Firewall configurado
- [ ] Monitoramento ativo

---

**🎉 PARABÉNS! Seu projeto Havoc está rodando em produção no Ubuntu!**

Para suporte adicional, verifique os logs ou consulte a documentação do Django e Docker.
