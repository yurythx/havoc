"""
Testes avançados para repositories do app accounts.
Testa queries complexas, transações e performance.
"""

from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.db import transaction, IntegrityError, connection
from django.db.models import Q, Count, Avg
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from datetime import timedelta
import time

from apps.accounts.models import VerificationCode
from apps.accounts.repositories.user_repository import DjangoUserRepository
from apps.accounts.repositories.verification_repository import DjangoVerificationRepository

User = get_user_model()


class UserRepositoryAdvancedTest(TestCase):
    """Testes avançados para UserRepository."""

    def setUp(self):
        """Configuração inicial para os testes."""
        self.repository = DjangoUserRepository()
        
        # Criar usuários de teste
        self.users = []
        for i in range(10):
            user = User.objects.create_user(
                email=f'user{i}@example.com',
                username=f'user{i}',
                password='testpass123',
                first_name=f'User{i}',
                last_name='Test',
                is_verified=(i % 2 == 0),  # Metade verificados
                is_active=(i % 3 != 0),   # Maioria ativos
                date_joined=timezone.now() - timedelta(days=i)
            )
            self.users.append(user)

    def test_get_users_with_complex_filters(self):
        """Testa busca de usuários com filtros complexos."""
        # Usuários verificados e ativos
        verified_active = self.repository.get_users(
            filters={'is_verified': True, 'is_active': True}
        )
        
        expected_count = sum(1 for u in self.users if u.is_verified and u.is_active)
        self.assertEqual(len(verified_active), expected_count)

    def test_get_users_with_q_objects(self):
        """Testa busca com objetos Q complexos."""
        # Usuários que começam com 'user1' ou 'user2'
        q_filter = Q(username__startswith='user1') | Q(username__startswith='user2')
        users = self.repository.get_users(q_filter=q_filter)
        
        expected_usernames = ['user1', 'user2']
        actual_usernames = [u.username for u in users]
        
        for username in expected_usernames:
            self.assertIn(username, actual_usernames)

    def test_get_users_with_ordering(self):
        """Testa busca com ordenação."""
        # Ordenar por data de criação (mais recente primeiro)
        users_desc = self.repository.get_users(ordering=['-date_joined'])
        
        # Verificar se está ordenado corretamente
        for i in range(len(users_desc) - 1):
            self.assertGreaterEqual(
                users_desc[i].date_joined,
                users_desc[i + 1].date_joined
            )

    def test_get_users_with_pagination(self):
        """Testa busca com paginação."""
        page_size = 3
        
        # Primeira página
        page1 = self.repository.get_users(limit=page_size, offset=0)
        self.assertEqual(len(page1), page_size)
        
        # Segunda página
        page2 = self.repository.get_users(limit=page_size, offset=page_size)
        self.assertEqual(len(page2), page_size)
        
        # Verificar que não há sobreposição
        page1_ids = {u.id for u in page1}
        page2_ids = {u.id for u in page2}
        self.assertEqual(len(page1_ids.intersection(page2_ids)), 0)

    def test_get_users_with_select_related(self):
        """Testa busca com select_related para otimização."""
        with self.assertNumQueries(1):
            users = self.repository.get_users(select_related=['groups'])
            # Acessar relacionamentos não deve gerar queries adicionais
            for user in users:
                _ = user.groups.all()

    def test_get_users_with_prefetch_related(self):
        """Testa busca com prefetch_related para otimização."""
        # Criar alguns grupos para teste
        from django.contrib.auth.models import Group
        group1 = Group.objects.create(name='Group1')
        group2 = Group.objects.create(name='Group2')
        
        self.users[0].groups.add(group1)
        self.users[1].groups.add(group1, group2)
        
        with self.assertNumQueries(2):  # 1 para users, 1 para groups
            users = self.repository.get_users(prefetch_related=['groups'])
            for user in users:
                _ = list(user.groups.all())

    def test_get_users_with_annotations(self):
        """Testa busca com anotações."""
        # Anotar com contagem de códigos de verificação
        for user in self.users[:3]:
            VerificationCode.objects.create(
                user=user,
                code='123456',
                code_type='registration'
            )
        
        users = self.repository.get_users(
            annotations={'verification_count': Count('verification_codes')}
        )
        
        # Verificar se anotação foi aplicada
        for user in users:
            self.assertTrue(hasattr(user, 'verification_count'))
            self.assertIsInstance(user.verification_count, int)

    def test_bulk_create_users(self):
        """Testa criação em lote de usuários."""
        users_data = [
            {
                'email': f'bulk{i}@example.com',
                'username': f'bulk{i}',
                'password': 'testpass123',
                'first_name': f'Bulk{i}',
                'last_name': 'User'
            }
            for i in range(5)
        ]
        
        created_users = self.repository.bulk_create_users(users_data)
        
        self.assertEqual(len(created_users), 5)
        for user in created_users:
            self.assertIsNotNone(user.id)

    def test_bulk_update_users(self):
        """Testa atualização em lote de usuários."""
        # Atualizar is_verified para todos os usuários
        updated_count = self.repository.bulk_update_users(
            filters={'is_verified': False},
            updates={'is_verified': True}
        )
        
        self.assertGreater(updated_count, 0)
        
        # Verificar se atualizações foram aplicadas
        unverified_count = User.objects.filter(is_verified=False).count()
        self.assertEqual(unverified_count, 0)

    def test_get_user_statistics(self):
        """Testa obtenção de estatísticas de usuários."""
        stats = self.repository.get_user_statistics()
        
        expected_keys = ['total_users', 'verified_users', 'active_users', 'recent_users']
        for key in expected_keys:
            self.assertIn(key, stats)
            self.assertIsInstance(stats[key], int)

    def test_search_users_by_text(self):
        """Testa busca textual de usuários."""
        # Buscar por nome
        results = self.repository.search_users('User1')
        usernames = [u.username for u in results]
        self.assertIn('user1', usernames)
        
        # Buscar por email
        results = self.repository.search_users('user2@example.com')
        emails = [u.email for u in results]
        self.assertIn('user2@example.com', emails)

    def test_get_users_by_date_range(self):
        """Testa busca de usuários por intervalo de datas."""
        start_date = timezone.now() - timedelta(days=5)
        end_date = timezone.now() - timedelta(days=2)
        
        users = self.repository.get_users_by_date_range(start_date, end_date)
        
        for user in users:
            self.assertGreaterEqual(user.date_joined, start_date)
            self.assertLessEqual(user.date_joined, end_date)


class VerificationRepositoryAdvancedTest(TestCase):
    """Testes avançados para VerificationRepository."""

    def setUp(self):
        """Configuração inicial para os testes."""
        self.repository = DjangoVerificationRepository()
        
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        
        # Criar códigos de teste
        self.codes = []
        for i in range(5):
            code = VerificationCode.objects.create(
                user=self.user,
                code=f'12345{i}',
                code_type='registration' if i % 2 == 0 else 'password_reset',
                created_at=timezone.now() - timedelta(hours=i)
            )
            self.codes.append(code)

    def test_get_codes_with_complex_filters(self):
        """Testa busca de códigos com filtros complexos."""
        # Códigos de registro não usados
        registration_codes = self.repository.get_verification_codes(
            filters={
                'code_type': 'registration',
                'is_used': False
            }
        )
        
        for code in registration_codes:
            self.assertEqual(code.code_type, 'registration')
            self.assertFalse(code.is_used)

    def test_get_codes_with_user_filter(self):
        """Testa busca de códigos por usuário."""
        codes = self.repository.get_verification_codes(
            filters={'user': self.user}
        )
        
        self.assertEqual(len(codes), 5)
        for code in codes:
            self.assertEqual(code.user, self.user)

    def test_get_latest_code_by_type(self):
        """Testa busca do código mais recente por tipo."""
        latest_registration = self.repository.get_latest_code(
            user=self.user,
            code_type='registration'
        )
        
        self.assertIsNotNone(latest_registration)
        self.assertEqual(latest_registration.code_type, 'registration')
        
        # Verificar se é realmente o mais recente
        all_registration_codes = VerificationCode.objects.filter(
            user=self.user,
            code_type='registration'
        ).order_by('-created_at')
        
        self.assertEqual(latest_registration, all_registration_codes.first())

    def test_cleanup_expired_codes(self):
        """Testa limpeza de códigos expirados."""
        # Criar códigos expirados
        expired_codes = []
        for i in range(3):
            code = VerificationCode.objects.create(
                user=self.user,
                code=f'exp{i}',
                code_type='registration',
                created_at=timezone.now() - timedelta(days=2)
            )
            expired_codes.append(code)
        
        # Executar limpeza
        deleted_count = self.repository.cleanup_expired_codes()
        
        self.assertGreater(deleted_count, 0)
        
        # Verificar se códigos expirados foram removidos
        for code in expired_codes:
            with self.assertRaises(ObjectDoesNotExist):
                VerificationCode.objects.get(id=code.id)

    def test_get_code_statistics(self):
        """Testa obtenção de estatísticas de códigos."""
        stats = self.repository.get_code_statistics()
        
        expected_keys = ['total_codes', 'used_codes', 'expired_codes', 'by_type']
        for key in expected_keys:
            self.assertIn(key, stats)

    def test_bulk_mark_codes_as_used(self):
        """Testa marcação em lote de códigos como usados."""
        code_ids = [code.id for code in self.codes[:3]]
        
        updated_count = self.repository.bulk_mark_as_used(code_ids)
        
        self.assertEqual(updated_count, 3)
        
        # Verificar se códigos foram marcados como usados
        for code_id in code_ids:
            code = VerificationCode.objects.get(id=code_id)
            self.assertTrue(code.is_used)

    def test_get_codes_by_date_range(self):
        """Testa busca de códigos por intervalo de datas."""
        start_date = timezone.now() - timedelta(hours=3)
        end_date = timezone.now() - timedelta(hours=1)
        
        codes = self.repository.get_codes_by_date_range(start_date, end_date)
        
        for code in codes:
            self.assertGreaterEqual(code.created_at, start_date)
            self.assertLessEqual(code.created_at, end_date)


class RepositoryPerformanceTest(TestCase):
    """Testes de performance para repositories."""

    def setUp(self):
        """Configuração inicial para os testes."""
        self.user_repo = DjangoUserRepository()
        self.verification_repo = DjangoVerificationRepository()
        
        # Criar dados de teste em quantidade
        self.users = []
        for i in range(100):
            user = User.objects.create_user(
                email=f'perf{i}@example.com',
                username=f'perf{i}',
                password='testpass123',
                first_name=f'Perf{i}',
                last_name='User'
            )
            self.users.append(user)

    def test_user_search_performance(self):
        """Testa performance da busca de usuários."""
        start_time = time.time()
        
        # Executar múltiplas buscas
        for i in range(10):
            users = self.user_repo.search_users(f'perf{i}')
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 10 buscas devem levar menos de 1 segundo
        self.assertLess(total_time, 1.0)

    def test_bulk_operations_performance(self):
        """Testa performance de operações em lote."""
        # Criar dados para bulk update
        user_ids = [u.id for u in self.users[:50]]
        
        start_time = time.time()
        
        # Bulk update
        updated_count = self.user_repo.bulk_update_users(
            filters={'id__in': user_ids},
            updates={'is_verified': True}
        )
        
        end_time = time.time()
        update_time = end_time - start_time
        
        self.assertEqual(updated_count, 50)
        # Bulk update deve ser rápido
        self.assertLess(update_time, 0.5)

    def test_query_optimization(self):
        """Testa otimização de queries."""
        # Criar códigos de verificação para alguns usuários
        for user in self.users[:10]:
            VerificationCode.objects.create(
                user=user,
                code='123456',
                code_type='registration'
            )
        
        # Buscar usuários com códigos usando select_related
        with self.assertNumQueries(1):
            users_with_codes = self.user_repo.get_users(
                filters={'verification_codes__isnull': False},
                select_related=['verification_codes']
            )
            
            # Acessar códigos não deve gerar queries adicionais
            for user in users_with_codes:
                _ = user.verification_codes.all()


class RepositoryTransactionTest(TransactionTestCase):
    """Testes de transações para repositories."""

    def setUp(self):
        """Configuração inicial para os testes."""
        self.user_repo = DjangoUserRepository()
        self.verification_repo = DjangoVerificationRepository()

    def test_atomic_user_creation(self):
        """Testa criação atômica de usuário."""
        user_data = {
            'email': 'atomic@example.com',
            'username': 'atomic',
            'password': 'testpass123',
            'first_name': 'Atomic',
            'last_name': 'User'
        }
        
        with transaction.atomic():
            user = self.user_repo.create_user(user_data)
            
            # Criar código de verificação na mesma transação
            code = self.verification_repo.create_verification_code(
                user=user,
                code_type='registration'
            )
            
            self.assertIsNotNone(user.id)
            self.assertIsNotNone(code.id)
            self.assertEqual(code.user, user)

    def test_rollback_on_error(self):
        """Testa rollback em caso de erro."""
        initial_user_count = User.objects.count()
        
        try:
            with transaction.atomic():
                # Criar usuário
                user = self.user_repo.create_user({
                    'email': 'rollback@example.com',
                    'username': 'rollback',
                    'password': 'testpass123'
                })
                
                # Forçar erro
                raise IntegrityError("Forced error")
                
        except IntegrityError:
            pass
        
        # Verificar se rollback funcionou
        final_user_count = User.objects.count()
        self.assertEqual(initial_user_count, final_user_count)

    def test_concurrent_user_creation(self):
        """Testa criação concorrente de usuários."""
        def create_user(email, username):
            try:
                return self.user_repo.create_user({
                    'email': email,
                    'username': username,
                    'password': 'testpass123'
                })
            except IntegrityError:
                return None
        
        # Tentar criar usuários com mesmo email simultaneamente
        user1 = create_user('concurrent@example.com', 'concurrent1')
        user2 = create_user('concurrent@example.com', 'concurrent2')
        
        # Apenas um deve ter sucesso
        successful_users = [u for u in [user1, user2] if u is not None]
        self.assertEqual(len(successful_users), 1)

    def test_savepoint_usage(self):
        """Testa uso de savepoints."""
        user = User.objects.create_user(
            email='savepoint@example.com',
            username='savepoint',
            password='testpass123'
        )
        
        with transaction.atomic():
            # Criar savepoint
            sid = transaction.savepoint()
            
            try:
                # Operação que pode falhar
                self.verification_repo.create_verification_code(
                    user=user,
                    code_type='invalid_type'  # Pode causar erro
                )
            except Exception:
                # Rollback para savepoint
                transaction.savepoint_rollback(sid)
            else:
                # Commit savepoint
                transaction.savepoint_commit(sid)
            
            # Operação que deve funcionar
            code = self.verification_repo.create_verification_code(
                user=user,
                code_type='registration'
            )
            
            self.assertIsNotNone(code)
