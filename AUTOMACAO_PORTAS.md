# 🤖 Automação de Resolução de Conflitos de Porta

## 📋 Visão Geral

O sistema de deploy do Havoc agora inclui **resolução automática de conflitos de porta**, eliminando a necessidade de intervenção manual quando portas estão ocupadas.

## 🔧 Como Funciona

### 1. **Detecção Automática**
- Escaneia `docker-compose.yml` e arquivos `.env`
- Identifica portas em uso no sistema
- Detecta conflitos automaticamente

### 2. **Resolução Inteligente**
- Encontra portas alternativas disponíveis
- Atualiza arquivos de configuração automaticamente
- Mantém mapeamentos internos dos containers

### 3. **Integração Transparente**
- Executa automaticamente durante o deploy
- Não requer configuração adicional
- Funciona com fallbacks se dependências não estiverem disponíveis

## 🚀 Uso Automático

### Deploy Normal
```bash
python deploy-auto.py
```

O sistema automaticamente:
1. ✅ Detecta conflitos de porta
2. ✅ Resolve conflitos automaticamente
3. ✅ Atualiza configurações
4. ✅ Prossegue com o deploy

### Teste Manual
```bash
# Testar apenas resolução de portas
python port_manager.py

# Testar integração completa
python test_port_automation.py
```

## 📊 Portas Gerenciadas

### Portas Padrão
- **8000** - Django Web Server
- **5432** - PostgreSQL (interno)
- **5433** - PostgreSQL (externo/Docker)
- **6379** - Redis
- **80/443** - Nginx

### Ranges de Portas Alternativas
- **Web:** 8000-8099
- **PostgreSQL:** 5433-5499
- **Redis:** 6379-6399
- **Nginx HTTP:** 8080-8199
- **Nginx HTTPS:** 8443-8499

## 🔍 Detecção de Conflitos

### Arquivos Monitorados
- `docker-compose.yml` - Mapeamentos de porta
- `.env` - Variáveis de porta
- `.env.docker` - Configuração Docker
- `.env.local` - Configuração local

### Padrões Detectados
```yaml
# docker-compose.yml
ports:
  - "8000:8000"  # Detectado
  - "5433:5432"  # Detectado
```

```env
# .env files
DB_PORT=5432        # Detectado
NGINX_PORT=80       # Detectado
```

## ⚙️ Resolução Automática

### Exemplo de Conflito
```
🔍 Detectando conflitos de porta...
⚠️  Detectados conflitos em 2 arquivo(s)

🐳 Resolvendo conflitos no docker-compose.yml...
   📝 web_port: 8000 → 8001
   📝 postgres_external: 5433 → 5434

📄 Resolvendo conflitos nos arquivos .env...
   📝 Atualizando .env.docker...
      DB_PORT: 5432 → 5434

✅ Todos os conflitos foram resolvidos automaticamente!
```

### Resultado
- **Antes:** `"8000:8000"` (conflito)
- **Depois:** `"8001:8000"` (sem conflito)
- **Acesso:** `http://localhost:8001`

## 🛠️ Configuração Avançada

### Personalizar Ranges de Porta
```python
# port_manager.py
PORT_RANGES = {
    'web': range(8000, 8100),        # Personalizar range
    'postgres_external': range(5433, 5500),
    # ...
}
```

### Desabilitar Automação
```python
# deploy-auto.py
PORT_MANAGER_AVAILABLE = False  # Força desabilitação
```

## 🔧 Troubleshooting

### Problema: Módulo yaml não encontrado
```bash
pip install PyYAML
```

### Problema: Encoding no Windows
- ✅ **Resolvido automaticamente** com fallbacks
- Usa caracteres ASCII quando Unicode falha

### Problema: Porta não liberada
```bash
# Verificar processos usando porta
netstat -ano | findstr :8000

# Matar processo (Windows)
taskkill /PID <PID> /F
```

## 📋 Logs e Monitoramento

### Logs de Resolução
```
📋 Resumo das correções aplicadas:
   • docker_web_port: 8000 → 8001
   • .env.docker_DB_PORT: 5432 → 5434

💡 Dicas importantes:
   • Use as novas portas para acessar os serviços
   • Os arquivos foram atualizados automaticamente
```

### Verificação Pós-Deploy
```bash
# Verificar portas em uso
python check_ports.py

# Status dos containers
docker-compose ps
```

## 🎯 Benefícios

### ✅ **Automação Completa**
- Zero intervenção manual
- Deploy sem falhas por conflito de porta
- Configuração automática

### ✅ **Inteligência**
- Detecta padrões complexos
- Escolhe portas adequadas
- Mantém consistência

### ✅ **Robustez**
- Funciona com/sem dependências
- Fallbacks para casos especiais
- Compatível com Windows/Linux

### ✅ **Transparência**
- Logs detalhados
- Resumo das alterações
- Fácil auditoria

## 🚀 Próximos Passos

1. **Deploy Automático:** `python deploy-auto.py`
2. **Verificar Logs:** Acompanhar resolução automática
3. **Acessar Aplicação:** Usar portas atualizadas
4. **Monitorar:** Verificar health checks

---

**🎉 Com esta automação, conflitos de porta são coisa do passado!**
