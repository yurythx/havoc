from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import os

User = get_user_model()

class Command(BaseCommand):
    help = 'Cria um superusuário padrão se não existir'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            default='admin@havoc.com',
            help='Email do superusuário (padrão: admin@havoc.com)',
        )
        parser.add_argument(
            '--username',
            type=str,
            default='admin',
            help='Username do superusuário (padrão: admin)',
        )
        parser.add_argument(
            '--password',
            type=str,
            default='admin123',
            help='Senha do superusuário (padrão: admin123)',
        )
        parser.add_argument(
            '--first-name',
            type=str,
            default='Admin',
            help='Primeiro nome (padrão: Admin)',
        )
        parser.add_argument(
            '--last-name',
            type=str,
            default='Havoc',
            help='Último nome (padrão: Havoc)',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Força criação mesmo se já existir superusuário',
        )

    def handle(self, *args, **options):
        email = options['email']
        username = options['username']
        password = options['password']
        first_name = options['first_name']
        last_name = options['last_name']
        force = options['force']

        # Verificar se já existe superusuário
        if not force and User.objects.filter(is_superuser=True).exists():
            existing_superuser = User.objects.filter(is_superuser=True).first()
            self.stdout.write(
                self.style.WARNING(
                    f'Superusuário já existe: {existing_superuser.email} ({existing_superuser.username})'
                )
            )
            return

        # Verificar se usuário com email já existe
        if User.objects.filter(email=email).exists():
            existing_user = User.objects.get(email=email)
            if not existing_user.is_superuser:
                # Promover usuário existente a superusuário
                existing_user.is_superuser = True
                existing_user.is_staff = True
                existing_user.is_verified = True
                existing_user.save()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Usuário existente {email} promovido a superusuário!'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'Superusuário {email} já existe!'
                    )
                )
            return

        # Verificar se username já existe
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.ERROR(
                    f'Username {username} já está em uso. Use --username para especificar outro.'
                )
            )
            return

        try:
            # Criar superusuário
            user = User.objects.create_superuser(
                email=email,
                password=password,
                username=username,
                first_name=first_name,
                last_name=last_name
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Superusuário criado com sucesso!\n'
                    f'Email: {user.email}\n'
                    f'Username: {user.username}\n'
                    f'Senha: {password}\n'
                    f'Nome: {user.first_name} {user.last_name}'
                )
            )
            
            # Mostrar informações de acesso
            self.stdout.write(
                self.style.HTTP_INFO(
                    '\n🔐 INFORMAÇÕES DE ACESSO:\n'
                    f'   URL Admin: /admin/\n'
                    f'   Email: {email}\n'
                    f'   Senha: {password}\n'
                    '\n⚠️  IMPORTANTE: Altere a senha padrão em produção!'
                )
            )

        except ValidationError as e:
            self.stdout.write(
                self.style.ERROR(f'Erro de validação: {e}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro ao criar superusuário: {e}')
            )

    def get_env_or_default(self, env_var, default):
        """Pega valor da variável de ambiente ou usa padrão"""
        return os.environ.get(env_var, default)
