#!/usr/bin/env python
"""
Teste simples de acesso a CSS
"""

import requests
import time

def test_css_access():
    print('🔍 TESTANDO ACESSO A CSS')
    print('=' * 40)
    
    time.sleep(2)
    
    try:
        response = requests.get('http://127.0.0.1:8000/static/css/main.css', timeout=5)
        print(f'Status: {response.status_code}')
        print(f'Content-Type: {response.headers.get("Content-Type", "N/A")}')
        print(f'Content-Length: {len(response.content)} bytes')
        
        if response.status_code == 200:
            content = response.text[:100]
            if 'html' in content.lower():
                print('❌ RETORNANDO HTML (problema)')
                print(f'Conteúdo: {content}')
            else:
                print('✅ RETORNANDO CSS (correto)')
                print(f'Conteúdo: {content}')
        else:
            print(f'❌ Status {response.status_code}')
            
    except Exception as e:
        print(f'❌ Erro: {e}')

if __name__ == '__main__':
    test_css_access()
