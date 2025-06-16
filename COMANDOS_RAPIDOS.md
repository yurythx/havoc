# ⚡ COMANDOS RÁPIDOS - DEPLOY HAVOC UBUNTU

## 🚀 **INSTALAÇÃO RÁPIDA**

### **1. Preparar servidor Ubuntu:**
```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependências automaticamente
chmod +x install_ubuntu.sh
./install_ubuntu.sh

# Aplicar grupo docker (obrigatório)
newgrp docker
```

### **2. Transferir projeto:**
```bash
# Via SCP (do seu computador)
scp -r /caminho/havoc usuario@ip-servidor:/home/usuario/

# Ou via Git (no servidor)
git clone https://github.com/seu-usuario/havoc.git
cd havoc
```

### **3. Configurar e fazer deploy:**
```bash
# Configurar ambiente
cp .env.docker .env
nano .env  # Editar configurações

# Gerar SECRET_KEY
python3 -c "from django.core.management.utils import get_random_secret_key; print('SECRET_KEY=' + get_random_secret_key())"

# Deploy completo
chmod +x deploy.sh
./deploy.sh deploy
```

---

## 🔧 **COMANDOS DE GERENCIAMENTO**

### **Deploy e Controle:**
```bash
# Deploy completo (primeira vez)
./deploy.sh deploy

# Deploy rápido (sem rebuild)
./deploy.sh quick

# Parar aplicação
./deploy.sh stop

# Ver logs em tempo real
./deploy.sh logs

# Limpar tudo
./deploy.sh clean
```

### **Docker Compose:**
```bash
# Status dos containers
docker-compose ps

# Logs específicos
docker-compose logs web
docker-compose logs db
docker-compose logs nginx

# Reiniciar serviços
docker-compose restart
docker-compose restart web

# Parar/Iniciar
docker-compose down
docker-compose up -d
```

---

## 🐍 **COMANDOS DJANGO**

### **Gerenciamento:**
```bash
# Shell Django
docker-compose exec web python manage.py shell

# Criar superusuário
docker-compose exec web python manage.py createsuperuser

# Migrações
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate

# Coletar estáticos
docker-compose exec web python manage.py collectstatic --clear

# Verificar sistema
docker-compose exec web python manage.py check
```

### **Comandos específicos do Havoc:**
```bash
# Sincronizar configurações
docker-compose exec web python manage.py sync_env_to_config

# Inicializar módulos
docker-compose exec web python manage.py shell -c "
from apps.config.services.module_service import ModuleService
service = ModuleService()
service.initialize_system()
"

# Verificar módulos
docker-compose exec web python manage.py shell -c "
from apps.config.models import AppModuleConfiguration
for m in AppModuleConfiguration.objects.all():
    print(f'{m.app_name}: {\"ATIVO\" if m.is_enabled else \"INATIVO\"}')
"
```

---

## 💾 **BACKUP E RESTORE**

### **Backup:**
```bash
# Backup do banco
docker-compose exec db pg_dump -U havoc_user havoc_prod > backup_$(date +%Y%m%d_%H%M%S).sql

# Backup completo
tar -czf backup_completo_$(date +%Y%m%d_%H%M%S).tar.gz \
    backup_*.sql media/ logs/ .env

# Backup automático (adicionar ao crontab)
echo "0 2 * * * cd /caminho/havoc && docker-compose exec db pg_dump -U havoc_user havoc_prod > backup_\$(date +\%Y\%m\%d_\%H\%M\%S).sql" | crontab -
```

### **Restore:**
```bash
# Restore do banco
docker-compose exec -T db psql -U havoc_user havoc_prod < backup.sql

# Restore com reset completo
docker-compose down -v
docker-compose up -d db
sleep 10
docker-compose exec -T db psql -U havoc_user havoc_prod < backup.sql
docker-compose up -d
```

---

## 🔍 **MONITORAMENTO E DEBUG**

### **Status e Recursos:**
```bash
# Status containers
docker-compose ps

# Recursos em tempo real
docker stats

# Logs do sistema
journalctl -f -u docker

# Espaço em disco
df -h
du -sh media/ logs/ staticfiles/

# Memória e CPU
free -h
htop
```

### **Debug de Problemas:**
```bash
# Verificar conectividade
curl -I http://localhost:8000

# Testar banco
docker-compose exec db psql -U havoc_user havoc_prod -c "SELECT version();"

# Verificar arquivos estáticos
docker-compose exec web ls -la /app/staticfiles/

# Verificar permissões
docker-compose exec web ls -la /app/

# Logs detalhados
docker-compose logs --tail=100 web
```

---

## 🌐 **CONFIGURAÇÃO DE DOMÍNIO**

### **DNS e Nginx:**
```bash
# Verificar DNS
nslookup seu-dominio.com

# Editar configuração Nginx
nano docker/nginx/default.conf

# Recarregar Nginx
docker-compose restart nginx

# Testar configuração
docker-compose exec nginx nginx -t
```

### **SSL com Let's Encrypt:**
```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx

# Obter certificado
sudo certbot --nginx -d seu-dominio.com

# Verificar renovação
sudo certbot renew --dry-run

# Renovação automática
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -
```

---

## 🔒 **SEGURANÇA**

### **Firewall:**
```bash
# Status do firewall
sudo ufw status

# Adicionar regra
sudo ufw allow from IP-ESPECIFICO to any port 8000

# Remover regra
sudo ufw delete allow 8000

# Reset firewall
sudo ufw --force reset
```

### **Atualizações:**
```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Atualizar imagens Docker
docker-compose pull
docker-compose up -d

# Limpar imagens antigas
docker system prune -f
```

---

## 🚨 **TROUBLESHOOTING RÁPIDO**

### **Problemas Comuns:**
```bash
# Container não inicia
docker-compose logs NOME_CONTAINER
docker-compose restart NOME_CONTAINER

# Porta ocupada
sudo netstat -tulpn | grep :8000
sudo kill -9 PID

# Sem espaço em disco
docker system prune -a -f
sudo apt autoremove -y

# Permissão negada
sudo chown -R $USER:$USER .
chmod +x deploy.sh

# Banco não conecta
docker-compose restart db
docker-compose logs db
```

### **Reset Completo:**
```bash
# CUIDADO: Apaga todos os dados
docker-compose down -v
docker system prune -a -f
./deploy.sh deploy
```

---

## 📱 **ACESSO RÁPIDO**

### **URLs Importantes:**
```bash
# Aplicação principal
http://SEU-IP:8000

# Admin Django
http://SEU-IP:8000/admin/
# Usuário: admin / Senha: admin123

# Configurações
http://SEU-IP:8000/config/

# Módulos
http://SEU-IP:8000/config/modulos/
```

### **Arquivos Importantes:**
```bash
# Configuração principal
nano .env

# Logs da aplicação
tail -f logs/django.log

# Configuração Nginx
nano docker/nginx/default.conf

# Docker Compose
nano docker-compose.yml
```

---

## 📞 **COMANDOS DE EMERGÊNCIA**

### **Parar Tudo:**
```bash
docker-compose down
sudo systemctl stop docker
```

### **Reiniciar Tudo:**
```bash
sudo systemctl restart docker
docker-compose up -d
```

### **Verificação Rápida:**
```bash
# Tudo funcionando?
curl -f http://localhost:8000 && echo "✅ OK" || echo "❌ ERRO"

# Containers rodando?
docker-compose ps | grep "Up" && echo "✅ Containers OK" || echo "❌ Problema nos containers"

# Espaço suficiente?
df -h / | awk 'NR==2{print $5}' | sed 's/%//' | awk '{if($1>90) print "❌ Pouco espaço"; else print "✅ Espaço OK"}'
```

---

**💡 DICA:** Salve este arquivo como favorito para acesso rápido aos comandos!
