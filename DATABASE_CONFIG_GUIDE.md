# 🗄️ GUIA DE CONFIGURAÇÃO DE BANCOS DE DADOS - HAVOC

## 📋 **VISÃO GERAL**

O sistema Havoc agora possui um módulo completo para gerenciar configurações de banco de dados, permitindo que você:

- ✅ **Configure múltiplos bancos** (SQLite, PostgreSQL, MySQL, Oracle)
- ✅ **Troque entre bancos** facilmente através da interface
- ✅ **Teste conexões** antes de ativar
- ✅ **Gerencie credenciais** de forma segura
- ✅ **Faça backup/restore** das configurações
- ✅ **Atualize arquivos .env** automaticamente

---

## 🚀 **COMO USAR**

### **1. Acessar Interface de Configurações**

**Opção 1: Interface Amigável**
```
http://127.0.0.1:8000/config/banco-dados/
```

**Opção 2: Admin Django**
```
http://127.0.0.1:8000/admin/config/databaseconfiguration/
```

### **2. Configurações Já Criadas**

O sistema já vem com 3 configurações pré-definidas:

#### **🗃️ SQLite Desenvolvimento** (Ativo/Padrão)
- **Tipo:** SQLite
- **Arquivo:** `db.sqlite3`
- **Status:** Ativo e Padrão
- **Uso:** Desenvolvimento local

#### **🐘 PostgreSQL Produção** (Inativo)
- **Tipo:** PostgreSQL
- **Banco:** `havoc_prod`
- **Host:** `localhost`
- **Porta:** `5432`
- **Status:** Template para produção

#### **🐬 MySQL Local** (Inativo)
- **Tipo:** MySQL
- **Banco:** `havoc_db`
- **Host:** `localhost`
- **Porta:** `3306`
- **Status:** Template para desenvolvimento

---

## 🔧 **FUNCIONALIDADES PRINCIPAIS**

### **1. ✅ Testar Conexões**
- Clique no botão **"Testar"** em qualquer configuração
- Verifica se as credenciais estão corretas
- Mostra status em tempo real
- Salva resultado do último teste

### **2. 🔄 Trocar Banco Ativo**
- Clique em **"Ativar"** na configuração desejada
- Sistema testa a conexão automaticamente
- Atualiza arquivo `.env` se necessário
- Define como configuração padrão

### **3. ➕ Criar Nova Configuração**
- Clique em **"Nova Configuração"**
- Preencha os dados do banco
- Teste a conexão antes de salvar
- Ative se desejar usar imediatamente

### **4. ⚡ Setup Rápido**
- Clique em **"Setup Rápido"**
- Escolha o tipo de banco
- Sistema cria template pré-configurado
- Edite apenas as credenciais

### **5. 💾 Backup e Restore**
- **Backup:** Exporta todas as configurações em JSON
- **Restore:** Importa configurações de arquivo
- Mantém histórico de mudanças
- Permite rollback se necessário

---

## 🛠️ **CONFIGURANDO DIFERENTES BANCOS**

### **🗃️ SQLite (Recomendado para Desenvolvimento)**
```python
Nome: "SQLite Local"
Tipo: SQLite
Arquivo: "db.sqlite3"
Host: (vazio)
Porta: (vazio)
Usuário: (vazio)
Senha: (vazio)
```

### **🐘 PostgreSQL (Recomendado para Produção)**
```python
Nome: "PostgreSQL Produção"
Tipo: PostgreSQL
Banco: "havoc_prod"
Host: "localhost" ou IP do servidor
Porta: "5432"
Usuário: "postgres"
Senha: "sua_senha_aqui"
```

### **🐬 MySQL**
```python
Nome: "MySQL Produção"
Tipo: MySQL
Banco: "havoc_db"
Host: "localhost" ou IP do servidor
Porta: "3306"
Usuário: "root"
Senha: "sua_senha_aqui"
```

### **🐳 PostgreSQL Docker**
```python
Nome: "PostgreSQL Docker"
Tipo: PostgreSQL
Banco: "havoc"
Host: "db" (nome do serviço)
Porta: "5432"
Usuário: "postgres"
Senha: "postgres"
```

---

## 🔐 **SEGURANÇA**

### **Senhas Criptografadas**
- Senhas são criptografadas automaticamente
- Usa chave baseada no `SECRET_KEY` do Django
- Não são visíveis na interface
- Descriptografadas apenas para conexão

### **Validações**
- Testa conexão antes de ativar
- Valida formato de portas
- Verifica campos obrigatórios por tipo
- Impede configurações inválidas

---

## 📊 **MONITORAMENTO**

### **Status da Conexão**
- ✅ **Verde:** Conexão bem-sucedida
- ❌ **Vermelho:** Erro de conexão
- ⚠️ **Amarelo:** Não testado

### **Logs de Atividade**
- Registra todas as mudanças
- Mostra quem fez alterações
- Timestamp de cada ação
- Histórico completo

---

## 🚀 **COMANDOS ÚTEIS**

### **Criar Configurações Iniciais**
```bash
python manage.py setup_database_configs
```

### **Forçar Recriação**
```bash
python manage.py setup_database_configs --force
```

### **Verificar Configurações Atuais**
```bash
python manage.py shell -c "
from apps.config.models import DatabaseConfiguration
configs = DatabaseConfiguration.objects.all()
for c in configs:
    print(f'{c.name}: {c.engine} - Default: {c.is_default}, Active: {c.is_active}')
"
```

---

## 🔄 **WORKFLOW RECOMENDADO**

### **Para Desenvolvimento:**
1. Use a configuração **SQLite** (já ativa)
2. Desenvolva normalmente
3. Teste com dados locais

### **Para Produção:**
1. Configure **PostgreSQL** ou **MySQL**
2. Teste a conexão
3. Ative a configuração
4. Execute migrações
5. Deploy da aplicação

### **Para Mudança de Banco:**
1. Crie nova configuração
2. Teste conexão
3. Execute migrações no novo banco
4. Ative nova configuração
5. Verifique funcionamento

---

## 🎯 **PRÓXIMOS PASSOS**

1. **Acesse a interface:** http://127.0.0.1:8000/config/banco-dados/
2. **Configure suas credenciais** nas configurações existentes
3. **Teste as conexões** antes de usar
4. **Ative a configuração** desejada
5. **Faça backup** das configurações importantes

---

## 🆘 **TROUBLESHOOTING**

### **Erro de Conexão**
- Verifique credenciais
- Confirme se o banco está rodando
- Teste conectividade de rede
- Verifique firewall/portas

### **Erro de Driver**
- Instale driver necessário:
  - PostgreSQL: `pip install psycopg2-binary`
  - MySQL: `pip install mysqlclient`

### **Erro de Migração**
- Execute migrações no banco ativo:
  ```bash
  python manage.py migrate
  ```

---

## 🎉 **CONCLUSÃO**

O sistema de configuração de bancos está **100% funcional** e pronto para uso! 

Você pode agora:
- ✅ **Gerenciar múltiplos bancos** facilmente
- ✅ **Trocar entre ambientes** sem editar código
- ✅ **Manter configurações seguras** e organizadas
- ✅ **Fazer backup/restore** quando necessário

**Acesse agora:** http://127.0.0.1:8000/config/banco-dados/ 🚀
