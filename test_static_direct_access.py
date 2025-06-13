#!/usr/bin/env python
"""
Teste direto de acesso a arquivos estáticos
"""

import os
import django
import time

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import Client
from django.conf import settings

def test_static_access():
    print('🔍 TESTE DIRETO DE ACESSO A ARQUIVOS ESTÁTICOS')
    print('=' * 60)
    
    # Aguardar servidor inicializar
    time.sleep(2)
    
    client = Client()
    
    # Testar arquivos específicos
    static_files = [
        '/static/css/main.css',
        '/static/css/django-theme.css', 
        '/static/js/main.js',
    ]
    
    print('📋 CONFIGURAÇÕES:')
    print(f'   DEBUG: {settings.DEBUG}')
    print(f'   STATIC_URL: {settings.STATIC_URL}')
    print(f'   STATICFILES_DIRS: {settings.STATICFILES_DIRS}')
    
    print(f'\n🧪 TESTANDO ACESSO VIA DJANGO CLIENT:')
    
    for static_file in static_files:
        try:
            response = client.get(static_file)
            print(f'📄 {static_file}')
            print(f'   Status: {response.status_code}')
            
            if response.status_code == 200:
                # Para FileResponse, usar streaming_content
                if hasattr(response, 'streaming_content'):
                    content = b''.join(response.streaming_content)
                    content_length = len(content)
                else:
                    content_length = len(response.content)
                
                content_type = response.get('Content-Type', 'N/A')
                print(f'   ✅ Sucesso ({content_length} bytes, {content_type})')
            else:
                print(f'   ❌ Falha')
                
        except Exception as e:
            print(f'   ❌ Erro: {e}')
    
    # Testar página principal
    print(f'\n🌐 TESTANDO PÁGINA PRINCIPAL:')
    try:
        response = client.get('/')
        print(f'📄 Página principal: Status {response.status_code}')
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Verificar referências específicas
            main_css_ref = 'href="/static/css/main.css"' in content
            django_theme_ref = 'href="/static/css/django-theme.css"' in content
            main_js_ref = 'src="/static/js/main.js"' in content
            
            print(f'   ✅ Página carregando ({len(content)} bytes)')
            print(f'   📊 main.css referenciado: {"✅" if main_css_ref else "❌"}')
            print(f'   📊 django-theme.css referenciado: {"✅" if django_theme_ref else "❌"}')
            print(f'   📊 main.js referenciado: {"✅" if main_js_ref else "❌"}')
            
        else:
            print(f'   ❌ Erro {response.status_code}')
            
    except Exception as e:
        print(f'   ❌ Erro: {e}')
    
    print(f'\n🎯 TESTE CONCLUÍDO!')

if __name__ == '__main__':
    test_static_access()
