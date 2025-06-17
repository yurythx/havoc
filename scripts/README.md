# 🔧 SCRIPTS DE DEPLOY - PROJETO HAVOC

## 📋 **SCRIPTS DISPONÍVEIS**

### **⭐ Scripts Recomendados:**

1. **`deploy_simples.ps1`** - **WINDOWS (RECOMENDADO)**
   - ✅ Totalmente funcional e testado
   - ✅ Interface amigável
   - ✅ Limpeza automática de ambiente
   - ✅ Geração robusta de SECRET_KEY

2. **`deploy_ubuntu.sh`** - **UBUNTU (RECOMENDADO)**
   - ✅ Instalação automática de dependências
   - ✅ Configuração de firewall
   - ✅ Detecção de IP para acesso remoto
   - ✅ Otimizado para Ubuntu

3. **`deploy_melhorado.sh`** - **LINUX/MAC (RECOMENDADO)**
   - ✅ Compatibilidade universal Unix
   - ✅ Múltiplos fallbacks para SECRET_KEY
   - ✅ Configuração robusta

### **📁 Scripts de Suporte:**

4. **`deploy.sh`** - Script original (backup)
5. **`install_ubuntu.sh`** - Instalação standalone Ubuntu

---

## 🚀 **COMO USAR**

### **🖥️ Windows:**
```powershell
# Deploy completo
.\deploy_simples.ps1 dev

# Verificar sistema
.\deploy_simples.ps1 check

# Limpar ambiente
.\deploy_simples.ps1 clean

# Gerar SECRET_KEY
.\deploy_simples.ps1 secret

# Ajuda
.\deploy_simples.ps1 help
```

### **🐧 Ubuntu:**
```bash
# Deploy completo
./deploy_ubuntu.sh dev

# Instalar dependências do sistema (como root)
sudo ./deploy_ubuntu.sh install

# Verificar sistema
./deploy_ubuntu.sh check

# Limpar ambiente
./deploy_ubuntu.sh clean

# Gerar SECRET_KEY
./deploy_ubuntu.sh secret

# Ajuda
./deploy_ubuntu.sh help
```

### **🐧 Linux/Mac:**
```bash
# Deploy completo
./deploy_melhorado.sh dev

# Verificar sistema
./deploy_melhorado.sh check

# Limpar ambiente
./deploy_melhorado.sh clean

# Gerar SECRET_KEY
./deploy_melhorado.sh secret

# Ajuda
./deploy_melhorado.sh help
```

---

## 🔧 **FUNCIONALIDADES DOS SCRIPTS**

### **✅ Funcionalidades Comuns:**
- **Limpeza de ambiente** - Remove variáveis conflitantes
- **Verificação de dependências** - Valida Python, pip, etc.
- **Geração de SECRET_KEY** - Múltiplos métodos seguros
- **Configuração automática** - Arquivo .env para desenvolvimento
- **Instalação de dependências** - pip install automático
- **Migrações de banco** - Django migrate
- **Criação de superusuário** - admin@havoc.com / admin123
- **Coleta de arquivos estáticos** - collectstatic
- **Verificação do sistema** - Django check

### **🐧 Funcionalidades Específicas Ubuntu:**
- **Instalação de dependências do sistema** - apt install automático
- **Configuração de firewall** - UFW porta 8000
- **Detecção de IP** - Configuração para acesso remoto
- **Configuração de rede** - localhost + IP local

---

## 🚨 **SOLUÇÃO DE PROBLEMAS**

### **❌ Erro: "SECRET_KEY é obrigatória"**
```bash
# Limpar ambiente e gerar nova chave
./deploy_simples.ps1 clean    # Windows
./deploy_ubuntu.sh clean      # Ubuntu
./deploy_melhorado.sh clean   # Linux/Mac

# Gerar nova SECRET_KEY
./deploy_simples.ps1 secret   # Windows
./deploy_ubuntu.sh secret     # Ubuntu
./deploy_melhorado.sh secret  # Linux/Mac
```

### **❌ Erro: "Permission denied"**
```bash
# Dar permissão de execução (Linux/Mac/Ubuntu)
chmod +x deploy_ubuntu.sh
chmod +x deploy_melhorado.sh
```

### **❌ Erro: "Dependências faltando"**
```bash
# Ubuntu - instalar dependências do sistema
sudo ./deploy_ubuntu.sh install

# Depois executar deploy normal
./deploy_ubuntu.sh dev
```

### **❌ Erro: "Porta 8000 inacessível"**
```bash
# Ubuntu - verificar firewall
sudo ufw status
sudo ufw allow 8000/tcp

# Verificar se servidor está rodando
ps aux | grep runserver
```

---

## 📊 **TESTES REALIZADOS**

### **✅ Scripts Testados e Aprovados:**
- ✅ **deploy_simples.ps1** - Windows PowerShell
- ✅ **deploy_ubuntu.sh** - Ubuntu 20.04+
- ✅ **deploy_melhorado.sh** - Linux/Mac genérico

### **✅ Funcionalidades Validadas:**
- ✅ **Geração SECRET_KEY** - 5 chaves únicas testadas
- ✅ **Limpeza ambiente** - Remove variáveis conflitantes
- ✅ **Verificação sistema** - Django check sem erros
- ✅ **Deploy completo** - Servidor funcionando
- ✅ **Comandos help/check/clean** - Todos funcionais

---

## 🎯 **FLUXO RECOMENDADO**

### **🚀 Para Novos Usuários:**
1. **Windows:** `.\deploy_simples.ps1 dev`
2. **Ubuntu:** `./deploy_ubuntu.sh dev`
3. **Linux/Mac:** `./deploy_melhorado.sh dev`

### **🔧 Para Desenvolvedores:**
1. **Verificar:** `.\deploy_simples.ps1 check`
2. **Limpar:** `.\deploy_simples.ps1 clean`
3. **Deploy:** `.\deploy_simples.ps1 dev`

### **🌐 Para Produção:**
1. **Preparar:** `sudo ./deploy_ubuntu.sh install`
2. **Configurar:** Editar `.env` para produção
3. **Deploy:** `./deploy_ubuntu.sh dev` ou usar Docker

---

## 📈 **ESTATÍSTICAS**

### **📊 Scripts Analisados:**
- **Total:** 10 scripts originais
- **Funcionais:** 6 scripts (60%)
- **Recomendados:** 3 scripts (30%)
- **Removidos:** 4 scripts problemáticos

### **✅ Cobertura de Plataformas:**
- ✅ **Windows** - deploy_simples.ps1
- ✅ **Ubuntu** - deploy_ubuntu.sh
- ✅ **Linux/Mac** - deploy_melhorado.sh

---

## 📝 **INFORMAÇÕES IMPORTANTES**

### **🔑 Credenciais Padrão:**
- **URL:** http://localhost:8000
- **Admin:** http://localhost:8000/admin/
- **Usuário:** admin@havoc.com
- **Senha:** admin123

### **📁 Arquivos Criados:**
- `.env` - Configurações de ambiente
- `db.sqlite3` - Banco de dados SQLite
- `staticfiles/` - Arquivos estáticos coletados

### **🌐 URLs Principais:**
- `/` - Homepage
- `/admin/` - Administração
- `/accounts/login/` - Login
- `/health/` - Health Check

---

**Última Atualização:** 17/06/2025  
**Status:** ✅ **SCRIPTS ORGANIZADOS E FUNCIONAIS**
