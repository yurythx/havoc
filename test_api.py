#!/usr/bin/env python
"""
Script para testar os endpoints da API de configuração de banco de dados
"""

import requests
import json

def test_endpoints():
    print('🔍 TESTANDO ENDPOINTS DA API')
    print('=' * 40)

    base_url = 'http://127.0.0.1:8000'
    
    # Testar endpoint de teste de conexão
    try:
        print('1. Testando POST /config/banco-dados/1/test/')
        response = requests.post(f'{base_url}/config/banco-dados/1/test/')
        print(f'   Status: {response.status_code}')
        
        if response.status_code == 200:
            data = response.json()
            print(f'   Sucesso: {data.get("success")}')
            print(f'   Mensagem: {data.get("message")}')
        else:
            print(f'   Erro: {response.text[:200]}')
            
    except Exception as e:
        print(f'   Erro na requisição: {e}')

    print()

    # Testar endpoint de preview
    try:
        print('2. Testando GET /config/banco-dados/1/preview/')
        response = requests.get(f'{base_url}/config/banco-dados/1/preview/')
        print(f'   Status: {response.status_code}')
        
        if response.status_code == 200:
            data = response.json()
            print(f'   Sucesso: {data.get("success")}')
            print(f'   Nome: {data.get("name")}')
            print(f'   Engine: {data.get("engine")}')
            print(f'   Banco: {data.get("name_db")}')
        else:
            print(f'   Erro: {response.text[:200]}')
            
    except Exception as e:
        print(f'   Erro na requisição: {e}')

    print()

    # Testar endpoint de aplicar produção
    try:
        print('3. Testando POST /config/banco-dados/2/aplicar-producao/')
        response = requests.post(f'{base_url}/config/banco-dados/2/aplicar-producao/')
        print(f'   Status: {response.status_code}')
        
        if response.status_code == 200:
            data = response.json()
            print(f'   Sucesso: {data.get("success")}')
            print(f'   Mensagem: {data.get("message")}')
            if data.get("config"):
                config = data["config"]
                print(f'   Engine: {config.get("DB_ENGINE")}')
                print(f'   Banco: {config.get("DB_NAME")}')
        else:
            print(f'   Erro: {response.text[:200]}')
            
    except Exception as e:
        print(f'   Erro na requisição: {e}')

    print()
    print('✅ Testes de API concluídos!')

if __name__ == '__main__':
    test_endpoints()
