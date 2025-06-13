#!/usr/bin/env python
"""
Script para testar carregamento de estilos
"""

import requests
import time

def test_styles():
    # Aguardar servidor inicializar
    time.sleep(3)

    print('🔍 TESTANDO CARREGAMENTO DE ESTILOS')
    print('=' * 50)

    # Lista de arquivos para testar
    files_to_test = [
        ('main.css', '/static/css/main.css'),
        ('django-theme.css', '/static/css/django-theme.css'),
        ('forms.css', '/static/css/forms.css'),
        ('main.js', '/static/js/main.js'),
        ('theme-toggle.js', '/static/js/theme-toggle.js'),
    ]

    base_url = 'http://127.0.0.1:8000'
    
    for name, path in files_to_test:
        try:
            response = requests.get(f'{base_url}{path}', timeout=5)
            print(f'📄 {name}: Status {response.status_code}')
            if response.status_code == 200:
                print(f'   ✅ Carregando corretamente ({len(response.content)} bytes)')
            else:
                print(f'   ❌ Erro {response.status_code}')
        except Exception as e:
            print(f'   ❌ Erro: {e}')

    # Testar página principal
    try:
        response = requests.get(f'{base_url}/', timeout=5)
        print(f'📄 Página principal: Status {response.status_code}')
        if response.status_code == 200:
            css_refs = response.text.count('static/css/')
            js_refs = response.text.count('static/js/')
            print(f'   ✅ Página carregando ({len(response.content)} bytes)')
            print(f'   📊 Referências CSS: {css_refs}')
            print(f'   📊 Referências JS: {js_refs}')
            
            # Verificar se Bootstrap está carregando
            if 'bootstrap' in response.text.lower():
                print('   ✅ Bootstrap referenciado')
            else:
                print('   ❌ Bootstrap não encontrado')
                
        else:
            print(f'   ❌ Erro {response.status_code}')
    except Exception as e:
        print(f'   ❌ Erro: {e}')

    print()
    print('🎯 TESTE CONCLUÍDO!')

if __name__ == '__main__':
    test_styles()
