#!/usr/bin/env python
"""
Teste completo do sistema - verifica todos os componentes
"""

import requests
import time
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import Client
from django.conf import settings

def test_complete_system():
    print('🔍 TESTE COMPLETO DO SISTEMA HAVOC')
    print('=' * 70)
    
    # Aguardar servidor inicializar
    time.sleep(3)
    
    base_url = 'http://127.0.0.1:8000'
    client = Client()
    
    # 1. TESTE DE CONFIGURAÇÕES
    print('\n📋 1. VERIFICANDO CONFIGURAÇÕES:')
    print(f'   DEBUG: {settings.DEBUG}')
    print(f'   STATIC_URL: {settings.STATIC_URL}')
    print(f'   STATICFILES_DIRS: {len(settings.STATICFILES_DIRS)} diretórios')
    print(f'   INSTALLED_APPS: {len(settings.INSTALLED_APPS)} apps')
    
    # 2. TESTE DE PÁGINAS PRINCIPAIS
    print('\n🌐 2. TESTANDO PÁGINAS PRINCIPAIS:')
    
    pages_to_test = [
        ('/', 'Página Principal'),
        ('/admin/', 'Django Admin'),
        ('/accounts/login/', 'Login'),
        ('/config/', 'Configurações'),
        ('/health/', 'Health Check'),
    ]
    
    page_results = []
    
    for url, name in pages_to_test:
        try:
            response = requests.get(f'{base_url}{url}', timeout=10, allow_redirects=False)
            status = response.status_code
            
            if status in [200, 302, 301]:
                result = '✅ OK'
                page_results.append(True)
            else:
                result = f'❌ {status}'
                page_results.append(False)
                
            print(f'   {name}: {result} ({status})')
            
        except Exception as e:
            print(f'   {name}: ❌ ERRO ({e})')
            page_results.append(False)
    
    # 3. TESTE DE ARQUIVOS ESTÁTICOS
    print('\n📄 3. TESTANDO ARQUIVOS ESTÁTICOS:')
    
    static_files = [
        ('/static/css/main.css', 'CSS Principal'),
        ('/static/css/django-theme.css', 'CSS Tema Django'),
        ('/static/css/forms.css', 'CSS Formulários'),
        ('/static/js/main.js', 'JavaScript Principal'),
        ('/static/js/theme-toggle.js', 'JavaScript Tema'),
    ]
    
    static_results = []
    
    for url, name in static_files:
        try:
            # Teste via Django Client
            django_response = client.get(url)
            django_status = django_response.status_code
            
            # Teste via requests
            requests_response = requests.get(f'{base_url}{url}', timeout=5)
            requests_status = requests_response.status_code
            
            if django_status == 200 and requests_status == 200:
                result = '✅ OK'
                static_results.append(True)
            elif django_status == 200:
                result = '🟡 Django OK, Requests FALHOU'
                static_results.append(False)
            else:
                result = '❌ FALHOU'
                static_results.append(False)
                
            print(f'   {name}: {result} (Django: {django_status}, Requests: {requests_status})')
            
        except Exception as e:
            print(f'   {name}: ❌ ERRO ({e})')
            static_results.append(False)
    
    # 4. TESTE DE BANCO DE DADOS
    print('\n🗄️ 4. TESTANDO BANCO DE DADOS:')
    
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result:
                print('   Conexão DB: ✅ OK')
                db_result = True
            else:
                print('   Conexão DB: ❌ FALHOU')
                db_result = False
    except Exception as e:
        print(f'   Conexão DB: ❌ ERRO ({e})')
        db_result = False
    
    # 5. TESTE DE APPS CUSTOMIZADOS
    print('\n📦 5. TESTANDO APPS CUSTOMIZADOS:')
    
    custom_apps = ['accounts', 'config', 'pages', 'articles']
    app_results = []
    
    for app in custom_apps:
        try:
            # Verificar se o app está instalado
            if f'apps.{app}' in settings.INSTALLED_APPS:
                # Tentar importar models
                exec(f'from apps.{app} import models')
                print(f'   App {app}: ✅ OK')
                app_results.append(True)
            else:
                print(f'   App {app}: ❌ NÃO INSTALADO')
                app_results.append(False)
        except Exception as e:
            print(f'   App {app}: ❌ ERRO ({e})')
            app_results.append(False)
    
    # 6. TESTE DE TEMPLATES
    print('\n🎨 6. TESTANDO TEMPLATES:')
    
    try:
        from django.template.loader import get_template
        
        templates_to_test = [
            'base.html',
            'pages/home.html',
            'accounts/login.html',
        ]
        
        template_results = []
        
        for template_name in templates_to_test:
            try:
                template = get_template(template_name)
                print(f'   {template_name}: ✅ OK')
                template_results.append(True)
            except Exception as e:
                print(f'   {template_name}: ❌ ERRO ({e})')
                template_results.append(False)
                
    except Exception as e:
        print(f'   Templates: ❌ ERRO GERAL ({e})')
        template_results = [False]
    
    # 7. RESUMO FINAL
    print('\n📊 7. RESUMO FINAL:')
    
    total_tests = 0
    passed_tests = 0
    
    # Contar resultados
    results = {
        'Páginas': page_results,
        'Arquivos Estáticos': static_results,
        'Banco de Dados': [db_result],
        'Apps Customizados': app_results,
        'Templates': template_results,
    }
    
    for category, category_results in results.items():
        category_passed = sum(category_results)
        category_total = len(category_results)
        total_tests += category_total
        passed_tests += category_passed
        
        percentage = (category_passed / category_total * 100) if category_total > 0 else 0
        status = '✅' if percentage == 100 else '🟡' if percentage >= 50 else '❌'
        
        print(f'   {category}: {status} {category_passed}/{category_total} ({percentage:.1f}%)')
    
    # Resultado geral
    overall_percentage = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f'\n🎯 RESULTADO GERAL:')
    print(f'   Total: {passed_tests}/{total_tests} testes passaram')
    print(f'   Percentual: {overall_percentage:.1f}%')
    
    if overall_percentage >= 90:
        print(f'   Status: 🟢 EXCELENTE - Sistema funcionando muito bem!')
    elif overall_percentage >= 70:
        print(f'   Status: 🟡 BOM - Sistema funcionando com pequenos problemas')
    elif overall_percentage >= 50:
        print(f'   Status: 🟠 REGULAR - Sistema funcionando mas precisa de correções')
    else:
        print(f'   Status: 🔴 CRÍTICO - Sistema com problemas sérios')
    
    print(f'\n🎉 TESTE COMPLETO FINALIZADO!')
    
    return overall_percentage

if __name__ == '__main__':
    test_complete_system()
