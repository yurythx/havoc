#!/usr/bin/env python
"""
Teste direto de arquivos estáticos usando Django Test Client
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import Client
from django.conf import settings
import time

def test_static_files():
    print('🔍 TESTE DIRETO DE ARQUIVOS ESTÁTICOS')
    print('=' * 60)
    
    # Aguardar servidor
    time.sleep(2)
    
    client = Client()
    
    # Lista de arquivos para testar
    static_files = [
        '/static/css/main.css',
        '/static/css/django-theme.css',
        '/static/css/forms.css',
        '/static/js/main.js',
        '/static/js/theme-toggle.js',
    ]
    
    print('📋 CONFIGURAÇÕES:')
    print(f'   DEBUG: {settings.DEBUG}')
    print(f'   STATIC_URL: {settings.STATIC_URL}')
    print(f'   STATICFILES_DIRS: {settings.STATICFILES_DIRS}')
    
    print(f'\n🧪 TESTANDO ARQUIVOS VIA DJANGO CLIENT:')
    
    for static_file in static_files:
        try:
            response = client.get(static_file)
            print(f'📄 {static_file}: Status {response.status_code}')
            
            if response.status_code == 200:
                content_length = len(response.content)
                content_type = response.get('Content-Type', 'N/A')
                print(f'   ✅ Sucesso ({content_length} bytes, {content_type})')
            elif response.status_code == 404:
                print(f'   ❌ Não encontrado')
                # Verificar se o arquivo existe fisicamente
                from django.contrib.staticfiles.finders import find
                found = find(static_file.replace('/static/', ''))
                if found:
                    print(f'   📁 Arquivo existe em: {found}')
                else:
                    print(f'   📁 Arquivo não encontrado pelos finders')
            else:
                print(f'   ⚠️ Status inesperado: {response.status_code}')
                
        except Exception as e:
            print(f'   ❌ Erro: {e}')
    
    # Testar página principal
    print(f'\n🌐 TESTANDO PÁGINA PRINCIPAL:')
    try:
        response = client.get('/')
        print(f'📄 Página principal: Status {response.status_code}')
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Verificar referências CSS
            css_refs = content.count('static/css/')
            js_refs = content.count('static/js/')
            bootstrap_refs = content.lower().count('bootstrap')
            
            print(f'   ✅ Página carregando ({len(content)} bytes)')
            print(f'   📊 Referências CSS: {css_refs}')
            print(f'   📊 Referências JS: {js_refs}')
            print(f'   📊 Bootstrap: {bootstrap_refs} referências')
            
            # Verificar se há links específicos
            if 'href="/static/css/main.css"' in content:
                print(f'   ✅ main.css referenciado corretamente')
            else:
                print(f'   ❌ main.css não encontrado na página')
                
        else:
            print(f'   ❌ Erro {response.status_code}')
            
    except Exception as e:
        print(f'   ❌ Erro: {e}')
    
    # Testar usando requests para comparar
    print(f'\n🌍 TESTANDO VIA REQUESTS (EXTERNO):')
    try:
        import requests
        
        # Testar um arquivo específico
        test_url = 'http://127.0.0.1:8000/static/css/main.css'
        response = requests.get(test_url, timeout=5)
        print(f'📄 {test_url}: Status {response.status_code}')
        
        if response.status_code == 200:
            print(f'   ✅ Sucesso via requests ({len(response.content)} bytes)')
        else:
            print(f'   ❌ Falha via requests')
            print(f'   📄 Conteúdo: {response.text[:200]}...')
            
    except Exception as e:
        print(f'   ❌ Erro requests: {e}')
    
    print(f'\n🎯 TESTE CONCLUÍDO!')

if __name__ == '__main__':
    test_static_files()
