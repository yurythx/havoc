"""
Comando para testar conexão com configuração de banco de dados específica
"""

from django.core.management.base import BaseCommand, CommandError
from apps.config.models.configuration_models import DatabaseConfiguration


class Command(BaseCommand):
    help = 'Testa a conexão com uma configuração de banco de dados específica'

    def add_arguments(self, parser):
        parser.add_argument(
            'config_id',
            type=int,
            help='ID da configuração de banco de dados para testar'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Mostrar informações detalhadas da configuração'
        )

    def handle(self, *args, **options):
        config_id = options['config_id']
        verbose = options['verbose']

        try:
            # Buscar configuração
            config = DatabaseConfiguration.objects.get(pk=config_id)
        except DatabaseConfiguration.DoesNotExist:
            raise CommandError(f'Configuração com ID {config_id} não encontrada')

        if verbose:
            self.stdout.write('\n' + '='*60)
            self.stdout.write(self.style.SUCCESS(f'TESTANDO CONFIGURAÇÃO: {config.name}'))
            self.stdout.write('='*60)
            self.stdout.write(f'ID: {config.pk}')
            self.stdout.write(f'Nome: {config.name}')
            self.stdout.write(f'Engine: {config.get_engine_display()}')
            self.stdout.write(f'Banco: {config.name_db}')
            
            if config.host:
                self.stdout.write(f'Host: {config.host}:{config.port}')
            
            if config.user:
                self.stdout.write(f'Usuário: {config.user}')
            
            self.stdout.write(f'Status: {"ATIVO" if config.is_active else "INATIVO"}')
            self.stdout.write(f'Padrão: {"SIM" if config.is_default else "NÃO"}')
            self.stdout.write('-' * 60)

        # Testar conexão
        self.stdout.write('Testando conexão...', ending='')
        
        try:
            success, message = config.test_connection()
            
            if success:
                self.stdout.write(self.style.SUCCESS(' ✓ SUCESSO'))
                if verbose:
                    self.stdout.write(f'Mensagem: {message}')
                    
                # Mostrar informações da conexão
                config_dict = config.get_config_dict()
                if verbose and config_dict:
                    self.stdout.write('\nConfiguração de conexão:')
                    for key, value in config_dict.items():
                        if key == 'PASSWORD' and value:
                            value = '***'
                        self.stdout.write(f'  {key}: {value}')
                        
            else:
                self.stdout.write(self.style.ERROR(' ✗ FALHOU'))
                self.stdout.write(self.style.ERROR(f'Erro: {message}'))
                
                if verbose:
                    self.stdout.write('\nPossíveis soluções:')
                    self.stdout.write('1. Verificar se o servidor de banco está rodando')
                    self.stdout.write('2. Verificar credenciais (usuário/senha)')
                    self.stdout.write('3. Verificar conectividade de rede (host/porta)')
                    self.stdout.write('4. Verificar se o banco de dados existe')
                    self.stdout.write('5. Verificar permissões do usuário')
                
                return
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(' ✗ ERRO INESPERADO'))
            self.stdout.write(self.style.ERROR(f'Exceção: {str(e)}'))
            return

        # Mostrar histórico de testes se verbose
        if verbose and config.last_tested_at:
            self.stdout.write(f'\nÚltimo teste: {config.last_tested_at.strftime("%d/%m/%Y %H:%M:%S")}')
            last_result = 'SUCESSO' if config.last_test_result else 'FALHOU'
            color = self.style.SUCCESS if config.last_test_result else self.style.ERROR
            self.stdout.write(f'Resultado anterior: {color(last_result)}')

        if verbose:
            self.stdout.write('='*60)
            
        # Sugestões baseadas no resultado
        if success:
            if not config.is_default:
                self.stdout.write('\n💡 Esta configuração pode ser aplicada como padrão:')
                self.stdout.write(f'   python manage.py apply_db_config {config.pk} --update-env')
        else:
            self.stdout.write('\n🔧 Para editar esta configuração:')
            self.stdout.write(f'   Acesse: /config/banco-dados/{config.pk}/editar/')
            
        self.stdout.write('')
