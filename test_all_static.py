#!/usr/bin/env python
"""
Teste rápido de todos os arquivos estáticos
"""

import requests
import time

def test_all_static():
    print('🔍 TESTE RÁPIDO - ARQUIVOS ESTÁTICOS')
    print('=' * 50)
    
    time.sleep(2)
    
    files = [
        '/static/css/main.css',
        '/static/css/django-theme.css',
        '/static/css/forms.css',
        '/static/js/main.js',
        '/static/js/theme-toggle.js',
    ]
    
    success = 0
    total = len(files)
    
    for file_url in files:
        try:
            response = requests.get(f'http://127.0.0.1:8000{file_url}', timeout=3)
            if response.status_code == 200:
                print(f'✅ {file_url} - OK ({len(response.content)} bytes)')
                success += 1
            else:
                print(f'❌ {file_url} - Status {response.status_code}')
        except Exception as e:
            print(f'❌ {file_url} - Erro: {e}')
    
    print(f'\n📊 RESULTADO: {success}/{total} arquivos OK')
    
    if success == total:
        print('🎉 TODOS OS ARQUIVOS ESTÁTICOS FUNCIONANDO!')
    else:
        print('⚠️ Alguns arquivos ainda com problema')

if __name__ == '__main__':
    test_all_static()
