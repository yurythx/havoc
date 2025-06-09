from django.core.management.base import BaseCommand
from django.contrib.auth import authenticate, get_user_model
from django.test import Client, RequestFactory
from apps.accounts.forms.authentication import FlexibleLoginForm

User = get_user_model()

class Command(BaseCommand):
    help = 'Testa o sistema de login com email e username'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            default='yurymenezes@hotmail.com',
            help='Email para testar',
        )
        parser.add_argument(
            '--username',
            type=str,
            default='yurymenezes',
            help='Username para testar',
        )
        parser.add_argument(
            '--password',
            type=str,
            default='admin123',
            help='Senha para testar',
        )

    def handle(self, *args, **options):
        email = options['email']
        username = options['username']
        password = options['password']

        self.stdout.write('='*60)
        self.stdout.write(self.style.SUCCESS('TESTE DE LOGIN COMPLETO'))
        self.stdout.write('='*60)

        # 1. Verificar se o usuário existe
        try:
            user = User.objects.get(email=email)
            self.stdout.write(f'✓ Usuário encontrado: {user.email}')
            self.stdout.write(f'  - Username: {user.username}')
            self.stdout.write(f'  - is_active: {user.is_active}')
            self.stdout.write(f'  - is_verified: {user.is_verified}')
            self.stdout.write(f'  - is_superuser: {user.is_superuser}')
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'✗ Usuário não encontrado: {email}'))
            return

        # 2. Testar autenticação direta
        self.stdout.write('\n' + '-'*40)
        self.stdout.write('TESTE DE AUTENTICAÇÃO DIRETA')
        self.stdout.write('-'*40)

        # Com email
        auth_email = authenticate(username=email, password=password)
        if auth_email:
            self.stdout.write(self.style.SUCCESS(f'✓ Autenticação com email: {auth_email}'))
        else:
            self.stdout.write(self.style.ERROR(f'✗ Falha na autenticação com email'))

        # Com username
        auth_username = authenticate(username=username, password=password)
        if auth_username:
            self.stdout.write(self.style.SUCCESS(f'✓ Autenticação com username: {auth_username}'))
        else:
            self.stdout.write(self.style.ERROR(f'✗ Falha na autenticação com username'))

        # 3. Testar formulário
        self.stdout.write('\n' + '-'*40)
        self.stdout.write('TESTE DE FORMULÁRIO')
        self.stdout.write('-'*40)

        rf = RequestFactory()
        request = rf.post('/login/')

        # Formulário com email
        form_data_email = {
            'username': email,
            'password': password,
            'remember_me': False
        }

        form_email = FlexibleLoginForm(request=request, data=form_data_email)
        if form_email.is_valid():
            user_form = form_email.get_user()
            self.stdout.write(self.style.SUCCESS(f'✓ Formulário com email válido: {user_form}'))
        else:
            self.stdout.write(self.style.ERROR(f'✗ Formulário com email inválido: {form_email.errors}'))

        # Formulário com username
        form_data_username = {
            'username': username,
            'password': password,
            'remember_me': False
        }

        form_username = FlexibleLoginForm(request=request, data=form_data_username)
        if form_username.is_valid():
            user_form = form_username.get_user()
            self.stdout.write(self.style.SUCCESS(f'✓ Formulário com username válido: {user_form}'))
        else:
            self.stdout.write(self.style.ERROR(f'✗ Formulário com username inválido: {form_username.errors}'))

        # 4. Testar view de login
        self.stdout.write('\n' + '-'*40)
        self.stdout.write('TESTE DE VIEW DE LOGIN')
        self.stdout.write('-'*40)

        client = Client()

        # Login com email
        response_email = client.post('/accounts/login/', {
            'username': email,
            'password': password,
            'submit': 'Entrar'
        })

        if response_email.status_code == 302:  # Redirect após login bem-sucedido
            self.stdout.write(self.style.SUCCESS(f'✓ Login via view com email: Redirecionado para {response_email.url}'))
        else:
            self.stdout.write(self.style.ERROR(f'✗ Login via view com email falhou: Status {response_email.status_code}'))

        # Logout para testar próximo login
        client.logout()

        # Login com username
        response_username = client.post('/accounts/login/', {
            'username': username,
            'password': password,
            'submit': 'Entrar'
        })

        if response_username.status_code == 302:  # Redirect após login bem-sucedido
            self.stdout.write(self.style.SUCCESS(f'✓ Login via view com username: Redirecionado para {response_username.url}'))
        else:
            self.stdout.write(self.style.ERROR(f'✗ Login via view com username falhou: Status {response_username.status_code}'))

        # 5. Resumo
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('RESUMO DOS TESTES'))
        self.stdout.write('='*60)

        tests = [
            ('Autenticação com email', auth_email is not None),
            ('Autenticação com username', auth_username is not None),
            ('Formulário com email', form_email.is_valid()),
            ('Formulário com username', form_username.is_valid()),
            ('View com email', response_email.status_code == 302),
            ('View com username', response_username.status_code == 302),
        ]

        passed = 0
        total = len(tests)

        for test_name, result in tests:
            if result:
                self.stdout.write(self.style.SUCCESS(f'✓ {test_name}'))
                passed += 1
            else:
                self.stdout.write(self.style.ERROR(f'✗ {test_name}'))

        self.stdout.write(f'\nResultado: {passed}/{total} testes passaram')

        if passed == total:
            self.stdout.write(self.style.SUCCESS('\n🎉 TODOS OS TESTES PASSARAM! O login está funcionando perfeitamente.'))
        else:
            self.stdout.write(self.style.WARNING(f'\n⚠️  {total - passed} teste(s) falharam. Verifique os problemas acima.'))
