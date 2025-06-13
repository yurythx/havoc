#!/usr/bin/env python
"""
Teste de acesso externo aos arquivos estáticos
"""

import requests
import time

def test_external_access():
    print('🌐 TESTE DE ACESSO EXTERNO A ARQUIVOS ESTÁTICOS')
    print('=' * 60)
    
    # Aguardar servidor inicializar
    time.sleep(3)
    
    base_url = 'http://127.0.0.1:8000'
    
    # Lista de arquivos para testar
    static_files = [
        '/static/css/main.css',
        '/static/css/django-theme.css',
        '/static/css/forms.css',
        '/static/js/main.js',
        '/static/js/theme-toggle.js',
    ]
    
    print('🧪 TESTANDO ACESSO VIA REQUESTS:')
    
    success_count = 0
    total_count = len(static_files)
    
    for static_file in static_files:
        try:
            url = f'{base_url}{static_file}'
            response = requests.get(url, timeout=10)
            
            print(f'📄 {static_file}')
            print(f'   URL: {url}')
            print(f'   Status: {response.status_code}')
            
            if response.status_code == 200:
                content_type = response.headers.get('Content-Type', 'N/A')
                content_length = len(response.content)
                print(f'   ✅ Sucesso ({content_length} bytes, {content_type})')
                success_count += 1
            else:
                print(f'   ❌ Falha')
                print(f'   Headers: {dict(response.headers)}')
                if response.text:
                    print(f'   Conteúdo: {response.text[:200]}...')
                
        except requests.exceptions.RequestException as e:
            print(f'   ❌ Erro de rede: {e}')
        except Exception as e:
            print(f'   ❌ Erro: {e}')
    
    # Testar página principal
    print(f'\n🌐 TESTANDO PÁGINA PRINCIPAL:')
    try:
        response = requests.get(f'{base_url}/', timeout=10)
        print(f'📄 Página principal: Status {response.status_code}')
        
        if response.status_code == 200:
            content = response.text
            
            # Verificar referências específicas
            main_css_ref = '/static/css/main.css' in content
            django_theme_ref = '/static/css/django-theme.css' in content
            main_js_ref = '/static/js/main.js' in content
            
            print(f'   ✅ Página carregando ({len(content)} bytes)')
            print(f'   📊 main.css referenciado: {"✅" if main_css_ref else "❌"}')
            print(f'   📊 django-theme.css referenciado: {"✅" if django_theme_ref else "❌"}')
            print(f'   📊 main.js referenciado: {"✅" if main_js_ref else "❌"}')
            
        else:
            print(f'   ❌ Erro {response.status_code}')
            
    except Exception as e:
        print(f'   ❌ Erro: {e}')
    
    # Resumo
    print(f'\n📊 RESUMO:')
    print(f'   Arquivos testados: {total_count}')
    print(f'   Sucessos: {success_count}')
    print(f'   Falhas: {total_count - success_count}')
    print(f'   Taxa de sucesso: {(success_count/total_count)*100:.1f}%')
    
    if success_count == total_count:
        print(f'\n🎉 TODOS OS ARQUIVOS ESTÁTICOS ESTÃO CARREGANDO CORRETAMENTE!')
    else:
        print(f'\n⚠️ ALGUNS ARQUIVOS NÃO ESTÃO CARREGANDO. VERIFIQUE A CONFIGURAÇÃO.')
    
    print(f'\n🎯 TESTE CONCLUÍDO!')

if __name__ == '__main__':
    test_external_access()
