#!/usr/bin/env python
"""
Script para diagnosticar problemas com arquivos estáticos
"""

import os
import django
from pathlib import Path

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.conf import settings
from django.contrib.staticfiles.finders import find
from django.contrib.staticfiles import finders

def diagnose_static():
    print('🔍 DIAGNÓSTICO DE ARQUIVOS ESTÁTICOS')
    print('=' * 60)
    
    # 1. Verificar configurações
    print('📋 CONFIGURAÇÕES:')
    print(f'   DEBUG: {settings.DEBUG}')
    print(f'   STATIC_URL: {settings.STATIC_URL}')
    print(f'   STATIC_ROOT: {settings.STATIC_ROOT}')
    print(f'   STATICFILES_DIRS: {settings.STATICFILES_DIRS}')
    print(f'   STATICFILES_FINDERS: {getattr(settings, "STATICFILES_FINDERS", "Padrão")}')
    
    # 2. Verificar se diretórios existem
    print(f'\n📁 DIRETÓRIOS:')
    for static_dir in settings.STATICFILES_DIRS:
        exists = Path(static_dir).exists()
        print(f'   {static_dir}: {"✅ Existe" if exists else "❌ Não existe"}')
        
        if exists:
            css_dir = Path(static_dir) / 'css'
            js_dir = Path(static_dir) / 'js'
            print(f'     css/: {"✅ Existe" if css_dir.exists() else "❌ Não existe"}')
            print(f'     js/: {"✅ Existe" if js_dir.exists() else "❌ Não existe"}')
            
            if css_dir.exists():
                css_files = list(css_dir.glob('*.css'))
                print(f'     Arquivos CSS: {len(css_files)}')
                for css_file in css_files[:5]:  # Mostrar apenas os primeiros 5
                    print(f'       - {css_file.name}')
    
    static_root_exists = Path(settings.STATIC_ROOT).exists()
    print(f'   {settings.STATIC_ROOT}: {"✅ Existe" if static_root_exists else "❌ Não existe"}')
    
    # 3. Testar finders
    print(f'\n🔍 TESTANDO FINDERS:')
    test_files = ['css/main.css', 'css/django-theme.css', 'js/main.js']
    
    for test_file in test_files:
        found = find(test_file)
        print(f'   {test_file}: {"✅ Encontrado" if found else "❌ Não encontrado"}')
        if found:
            print(f'     Caminho: {found}')
    
    # 4. Listar todos os finders
    print(f'\n🔧 FINDERS ATIVOS:')
    for finder in finders.get_finders():
        print(f'   - {finder.__class__.__name__}')
        if hasattr(finder, 'locations'):
            for location in finder.locations:
                print(f'     📁 {location}')
    
    # 5. Verificar URLs
    print(f'\n🌐 CONFIGURAÇÃO DE URLs:')
    try:
        from django.urls import reverse
        from django.test import Client
        
        client = Client()
        
        # Testar se a URL de static está configurada
        test_url = '/static/css/main.css'
        print(f'   Testando: {test_url}')
        
        # Simular requisição
        response = client.get(test_url)
        print(f'   Status: {response.status_code}')
        
        if response.status_code == 404:
            print('   ❌ Arquivo não encontrado via Django')
        elif response.status_code == 200:
            print('   ✅ Arquivo encontrado via Django')
        else:
            print(f'   ⚠️ Status inesperado: {response.status_code}')
            
    except Exception as e:
        print(f'   ❌ Erro ao testar URLs: {e}')
    
    # 6. Verificar middleware
    print(f'\n🔧 MIDDLEWARE:')
    for middleware in settings.MIDDLEWARE:
        print(f'   - {middleware}')
    
    print(f'\n🎯 DIAGNÓSTICO CONCLUÍDO!')

if __name__ == '__main__':
    diagnose_static()
