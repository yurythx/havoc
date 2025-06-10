#!/usr/bin/env python
"""
Script para testar todas as rotas do app config
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

User = get_user_model()

def test_config_routes():
    """Testa todas as rotas do config"""
    client = Client()
    
    # Criar usuário de teste se não existir
    try:
        user = User.objects.get(email='admin@test.com')
    except User.DoesNotExist:
        user = User.objects.create_user(
            email='admin@test.com',
            username='admin_test',
            password='testpass123',
            is_staff=True,
            is_superuser=True
        )
    
    # Fazer login
    client.login(username='admin_test', password='testpass123')
    
    # Lista de rotas para testar
    routes_to_test = [
        ('config:dashboard', {}),
        ('config:user_list', {}),
        ('config:user_create', {}),
        ('config:email_config', {}),
        ('config:email_test', {}),
        ('config:email_templates', {}),
        ('config:email_stats', {}),
        ('config:system_config', {}),
        ('config:environment_variables', {}),
        ('config:export_config', {}),
        ('config:import_config', {}),
        ('config:backup_config', {}),
        ('config:cache_management', {}),
        ('config:system_logs', {}),
    ]
    
    print("🧪 Testando rotas do config...")
    print("=" * 50)
    
    results = []
    
    for route_name, kwargs in routes_to_test:
        try:
            url = reverse(route_name, kwargs=kwargs)
            response = client.get(url)
            
            status = "✅ OK" if response.status_code in [200, 302] else f"❌ ERROR ({response.status_code})"
            
            print(f"{route_name:<30} {url:<30} {status}")
            
            results.append({
                'route': route_name,
                'url': url,
                'status_code': response.status_code,
                'success': response.status_code in [200, 302]
            })
            
        except Exception as e:
            print(f"{route_name:<30} {'ERROR':<30} ❌ {str(e)}")
            results.append({
                'route': route_name,
                'url': 'ERROR',
                'status_code': 0,
                'success': False,
                'error': str(e)
            })
    
    print("\n" + "=" * 50)
    print("📊 RESUMO DOS TESTES")
    print("=" * 50)
    
    successful = sum(1 for r in results if r['success'])
    total = len(results)
    
    print(f"✅ Rotas funcionando: {successful}/{total}")
    print(f"❌ Rotas com problemas: {total - successful}/{total}")
    
    if total - successful > 0:
        print("\n🔧 ROTAS COM PROBLEMAS:")
        for result in results:
            if not result['success']:
                error_msg = result.get('error', f"Status {result['status_code']}")
                print(f"   • {result['route']}: {error_msg}")
    
    print("\n🎯 TESTE CONCLUÍDO!")
    
    return results

if __name__ == '__main__':
    test_config_routes()
