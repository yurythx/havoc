#!/usr/bin/env python
"""
Script para testar o sistema de verificação por email
"""

import os
import sys
import django
from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.accounts.models import VerificationCode
from apps.accounts.services.registration_service import RegistrationService
from apps.accounts.services.password_service import PasswordService
from apps.accounts.repositories.user_repository import DjangoUserRepository
from apps.accounts.repositories.verification_repository import DjangoVerificationRepository
from apps.accounts.notifications.email_notification import EmailNotificationService

User = get_user_model()

def test_registration_email_verification():
    """Testa o sistema de verificação por email no registro"""
    print("🧪 TESTANDO SISTEMA DE VERIFICAÇÃO POR EMAIL")
    print("=" * 60)
    
    # Limpar dados de teste anteriores
    test_email = "teste.verificacao@example.com"
    User.objects.filter(email=test_email).delete()
    VerificationCode.objects.filter(user__email=test_email).delete()
    
    print(f"📧 Testando registro com email: {test_email}")
    
    # 1. Testar registro de usuário
    print("\n1️⃣ TESTE DE REGISTRO")
    print("-" * 30)
    
    service = RegistrationService(
        user_repository=DjangoUserRepository(),
        verification_repository=DjangoVerificationRepository(),
        notification_service=EmailNotificationService()
    )
    
    try:
        user = service.register_user(
            email=test_email,
            password="senha123456",
            first_name="Teste",
            last_name="Verificação",
            username="teste_verificacao"
        )
        
        print(f"✅ Usuário criado: {user.email}")
        print(f"✅ Verificado: {user.is_verified}")
        
        # Verificar se código foi criado
        verification_codes = VerificationCode.objects.filter(
            user=user,
            code_type=VerificationCode.REGISTRATION
        )
        
        if verification_codes.exists():
            code = verification_codes.first()
            print(f"✅ Código de verificação criado: {code.code}")
            print(f"✅ Tipo: {code.get_code_type_display()}")
            print(f"✅ Expira em: {code.expires_at}")
            print(f"✅ Expirado: {code.is_expired()}")
            
            # 2. Testar confirmação do registro
            print("\n2️⃣ TESTE DE CONFIRMAÇÃO")
            print("-" * 30)
            
            # Testar código correto
            if service.confirm_registration(test_email, code.code):
                print("✅ Confirmação com código correto: SUCESSO")
                
                # Verificar se usuário foi verificado
                user.refresh_from_db()
                print(f"✅ Usuário verificado após confirmação: {user.is_verified}")
                
                # Verificar se código foi removido
                remaining_codes = VerificationCode.objects.filter(
                    user=user,
                    code_type=VerificationCode.REGISTRATION
                ).count()
                print(f"✅ Códigos restantes após confirmação: {remaining_codes}")
                
            else:
                print("❌ Confirmação com código correto: FALHOU")
            
            # Testar código incorreto
            if not service.confirm_registration(test_email, "999999"):
                print("✅ Confirmação com código incorreto: REJEITADA (correto)")
            else:
                print("❌ Confirmação com código incorreto: ACEITA (erro)")
                
        else:
            print("❌ Código de verificação NÃO foi criado")
            
    except Exception as e:
        print(f"❌ Erro no registro: {e}")
    
    print("\n" + "=" * 60)

def test_password_reset_email_verification():
    """Testa o sistema de verificação por email na recuperação de senha"""
    print("\n🔒 TESTANDO RECUPERAÇÃO DE SENHA POR EMAIL")
    print("=" * 60)
    
    test_email = "teste.senha@example.com"
    
    # Criar usuário verificado para teste
    User.objects.filter(email=test_email).delete()
    user = User.objects.create_user(
        email=test_email,
        password="senha_antiga",
        first_name="Teste",
        last_name="Senha",
        username="teste_senha",
        is_verified=True
    )
    
    print(f"📧 Testando recuperação para: {test_email}")
    
    # 1. Testar solicitação de reset
    print("\n1️⃣ TESTE DE SOLICITAÇÃO DE RESET")
    print("-" * 40)
    
    password_service = PasswordService(
        user_repository=DjangoUserRepository(),
        verification_repository=DjangoVerificationRepository(),
        notification_service=EmailNotificationService()
    )
    
    try:
        if password_service.request_password_reset(test_email):
            print("✅ Solicitação de reset: SUCESSO")
            
            # Verificar se código foi criado
            verification_codes = VerificationCode.objects.filter(
                user=user,
                code_type=VerificationCode.PASSWORD_RESET
            )
            
            if verification_codes.exists():
                code = verification_codes.first()
                print(f"✅ Código de reset criado: {code.code}")
                print(f"✅ Tipo: {code.get_code_type_display()}")
                print(f"✅ Expira em: {code.expires_at}")
                
                # 2. Testar confirmação do reset
                print("\n2️⃣ TESTE DE CONFIRMAÇÃO DE RESET")
                print("-" * 40)
                
                new_password = "nova_senha_123"
                
                # Testar código correto
                if password_service.confirm_password_reset(test_email, code.code, new_password):
                    print("✅ Reset com código correto: SUCESSO")
                    
                    # Verificar se senha foi alterada
                    user.refresh_from_db()
                    if user.check_password(new_password):
                        print("✅ Senha foi alterada corretamente")
                    else:
                        print("❌ Senha NÃO foi alterada")
                    
                    # Verificar se código foi removido
                    remaining_codes = VerificationCode.objects.filter(
                        user=user,
                        code_type=VerificationCode.PASSWORD_RESET
                    ).count()
                    print(f"✅ Códigos restantes após reset: {remaining_codes}")
                    
                else:
                    print("❌ Reset com código correto: FALHOU")
                
                # Testar código incorreto (criar novo código primeiro)
                password_service.request_password_reset(test_email)
                if not password_service.confirm_password_reset(test_email, "999999", "outra_senha"):
                    print("✅ Reset com código incorreto: REJEITADO (correto)")
                else:
                    print("❌ Reset com código incorreto: ACEITO (erro)")
                    
            else:
                print("❌ Código de reset NÃO foi criado")
                
        else:
            print("❌ Solicitação de reset: FALHOU")
            
    except Exception as e:
        print(f"❌ Erro no reset de senha: {e}")
    
    print("\n" + "=" * 60)

def test_code_generation():
    """Testa a geração de códigos de 6 dígitos"""
    print("\n🔢 TESTANDO GERAÇÃO DE CÓDIGOS")
    print("=" * 60)
    
    repo = DjangoVerificationRepository()
    
    # Criar usuário de teste
    test_user = User.objects.create_user(
        email="teste.codigo@example.com",
        password="senha123",
        username="teste_codigo"
    )
    
    print("Gerando 10 códigos para verificar formato...")
    
    for i in range(10):
        code = repo.create_verification_code(test_user, VerificationCode.REGISTRATION)
        
        # Verificar se é um código de 6 dígitos
        is_6_digits = len(code) == 6 and code.isdigit()
        is_valid_range = 100000 <= int(code) <= 999999
        
        print(f"Código {i+1}: {code} - 6 dígitos: {is_6_digits} - Range válido: {is_valid_range}")
        
        if not (is_6_digits and is_valid_range):
            print(f"❌ Código inválido: {code}")
            break
    else:
        print("✅ Todos os códigos são válidos (6 dígitos)")
    
    # Limpar
    test_user.delete()
    
    print("\n" + "=" * 60)

def test_email_templates():
    """Testa se os templates de email existem e estão corretos"""
    print("\n📧 TESTANDO TEMPLATES DE EMAIL")
    print("=" * 60)
    
    from django.template.loader import get_template
    from django.template import Context
    
    templates_to_test = [
        ('accounts/emails/registration_confirmation.html', 'Confirmação de Registro'),
        ('accounts/emails/password_reset.html', 'Reset de Senha'),
    ]
    
    test_context = {
        'email': 'teste@example.com',
        'code': '123456',
        'site_name': 'HAVOC'
    }
    
    for template_path, description in templates_to_test:
        try:
            template = get_template(template_path)
            rendered = template.render(test_context)
            
            # Verificar se o código aparece no template
            if '123456' in rendered:
                print(f"✅ {description}: Template OK - Código aparece no email")
            else:
                print(f"❌ {description}: Template OK - Código NÃO aparece no email")
                
            # Verificar se tem elementos essenciais
            has_code_display = 'code' in rendered.lower()
            has_instructions = any(word in rendered.lower() for word in ['digite', 'use', 'código'])
            
            print(f"   - Exibe código: {has_code_display}")
            print(f"   - Tem instruções: {has_instructions}")
            
        except Exception as e:
            print(f"❌ {description}: Erro ao carregar template - {e}")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    print("🚀 INICIANDO TESTES DO SISTEMA DE VERIFICAÇÃO POR EMAIL")
    print("=" * 80)
    
    # Executar todos os testes
    test_code_generation()
    test_email_templates()
    test_registration_email_verification()
    test_password_reset_email_verification()
    
    print("\n🎯 TESTES CONCLUÍDOS!")
    print("=" * 80)
