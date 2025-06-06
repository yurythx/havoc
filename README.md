# 🔐 Havoc - Sistema de Autenticação Django

Sistema completo de autenticação e gerenciamento de usuários desenvolvido em Django com arquitetura limpa e padrões de design.

## 🚀 **Características**

- ✅ **Registro de usuários** com verificação por email
- ✅ **Sistema de login/logout** seguro
- ✅ **Redefinição de senha** via código por email
- ✅ **Perfis de usuário** editáveis
- ✅ **Arquitetura limpa** com Services, Repositories e Interfaces
- ✅ **Validações robustas** e tratamento de erros
- ✅ **Rate limiting** (quando django-ratelimit estiver instalado)
- ✅ **Configurações de segurança** para produção

## 📋 **Requisitos**

- Python 3.8+
- Django 5.2+
- SQLite (padrão) ou PostgreSQL/MySQL

## 🛠️ **Instalação**

### 1. Clone o repositório
```bash
git clone <url-do-repositorio>
cd havoc
```

### 2. Crie um ambiente virtual
```bash
python -m venv env
source env/bin/activate  # Linux/Mac
# ou
env\Scripts\activate     # Windows
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

### 5. Execute as migrações
```bash
python manage.py migrate
```

### 6. Crie um superusuário
```bash
python manage.py createsuperuser
```

### 7. Execute o servidor
```bash
python manage.py runserver
```

## 🏗️ **Arquitetura**

O projeto segue os princípios de **Clean Architecture** e **SOLID**:

```
apps/accounts/
├── interfaces/          # Contratos (Interfaces)
│   ├── services.py      # IAuthService, IRegistrationService, etc.
│   ├── repositories.py  # IUserRepository, IVerificationRepository
│   └── notifications.py # INotificationService
├── services/            # Regras de negócio
│   ├── auth_service.py
│   ├── registration_service.py
│   └── password_service.py
├── repositories/        # Acesso a dados
│   ├── user_repository.py
│   └── verification_repository.py
├── models/              # Modelos de dados
│   ├── user.py
│   └── verification.py
├── views/               # Controllers
├── forms/               # Formulários
└── notifications/       # Serviços de notificação
```

## 🔧 **Configuração**

### Variáveis de Ambiente (.env)

```env
# Django
DJANGO_SECRET_KEY=sua-chave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Email (para produção)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu@email.com
EMAIL_HOST_PASSWORD=sua-senha-de-app
DEFAULT_FROM_EMAIL=seu@email.com
```

## 📚 **URLs Disponíveis**

| URL | Descrição |
|-----|-----------|
| `/admin/` | Django Admin |
| `/accounts/registro/` | Registro de usuário |
| `/accounts/verificacao/` | Verificação de email |
| `/accounts/login/` | Login |
| `/accounts/logout/` | Logout |
| `/accounts/redefinir-senha/` | Solicitar reset de senha |
| `/accounts/confirmar-senha/<slug>/` | Confirmar reset de senha |
| `/accounts/perfil/<slug>/` | Visualizar perfil |
| `/accounts/perfil/<slug>/editar/` | Editar perfil |

## 🧪 **Testes**

```bash
# Executar todos os testes
python manage.py test

# Executar testes específicos
python manage.py test apps.accounts.tests.test_services
```

## 🔒 **Segurança**

O projeto implementa várias medidas de segurança:

- **CSRF Protection** habilitado
- **XSS Protection** configurado
- **Secure Headers** implementados
- **Rate Limiting** (opcional)
- **Validação de entrada** rigorosa
- **Senhas hasheadas** com Django's PBKDF2

## 📝 **Desenvolvimento**

### Adicionando novas funcionalidades

1. **Crie uma interface** em `interfaces/`
2. **Implemente o serviço** em `services/`
3. **Crie o repositório** (se necessário) em `repositories/`
4. **Adicione a view** em `views/`
5. **Configure a URL** em `urls.py`

### Exemplo: Novo serviço

```python
# interfaces/services.py
class IEmailService(ABC):
    @abstractmethod
    def send_welcome_email(self, user): pass

# services/email_service.py
class EmailService(IEmailService):
    def send_welcome_email(self, user):
        # Implementação
        pass
```

## 🤝 **Contribuição**

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📄 **Licença**

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🆘 **Suporte**

Se encontrar problemas ou tiver dúvidas:

1. Verifique a documentação em `CORREÇÕES_IMPLEMENTADAS.md`
2. Abra uma issue no GitHub
3. Consulte os logs do Django para debugging

---

**Desenvolvido com ❤️ usando Django e Clean Architecture**
