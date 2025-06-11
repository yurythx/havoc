#!/usr/bin/env python
"""
Script para executar todos os testes do projeto Havoc com relatório de coverage.
"""

import os
import sys
import subprocess
import time
from datetime import datetime

def run_command(command, description):
    """Executa um comando e retorna o resultado."""
    print(f"\n{'='*60}")
    print(f"🔄 {description}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutos timeout
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        if result.returncode == 0:
            print(f"✅ {description} - Concluído em {duration:.2f}s")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"❌ {description} - Falhou em {duration:.2f}s")
            if result.stderr:
                print("ERRO:", result.stderr)
            if result.stdout:
                print("SAÍDA:", result.stdout)
        
        return result.returncode == 0, result.stdout, result.stderr
        
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - Timeout após 5 minutos")
        return False, "", "Timeout"
    except Exception as e:
        print(f"💥 {description} - Erro: {e}")
        return False, "", str(e)

def main():
    """Função principal."""
    print("🚀 HAVOC - Execução Completa de Testes")
    print(f"📅 Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verificar se estamos no diretório correto
    if not os.path.exists('manage.py'):
        print("❌ Erro: manage.py não encontrado. Execute este script na raiz do projeto.")
        sys.exit(1)
    
    # Lista de comandos de teste
    test_commands = [
        {
            'command': 'python manage.py test apps.accounts.tests.test_models --keepdb -v 1',
            'description': 'Testes de Modelos - Accounts'
        },
        {
            'command': 'python manage.py test apps.config.tests.test_models --keepdb -v 1',
            'description': 'Testes de Modelos - Config'
        },
        {
            'command': 'python manage.py test apps.articles.tests.test_models --keepdb -v 1',
            'description': 'Testes de Modelos - Articles'
        },
        {
            'command': 'python manage.py test apps.accounts.tests.test_forms --keepdb -v 1',
            'description': 'Testes de Formulários - Accounts'
        },
        {
            'command': 'python manage.py test apps.accounts.tests.test_integration --keepdb -v 1',
            'description': 'Testes de Integração - Accounts'
        },
        {
            'command': 'python manage.py test apps.accounts.tests.test_backends --keepdb -v 1',
            'description': 'Testes de Backends - Accounts'
        }
    ]
    
    # Executar testes individuais
    results = []
    total_tests = 0
    
    for test_info in test_commands:
        success, stdout, stderr = run_command(
            test_info['command'], 
            test_info['description']
        )
        
        # Extrair número de testes do output
        if 'Ran ' in stdout:
            try:
                test_count = int(stdout.split('Ran ')[1].split(' test')[0])
                total_tests += test_count
            except:
                pass
        
        results.append({
            'description': test_info['description'],
            'success': success,
            'stdout': stdout,
            'stderr': stderr
        })
    
    # Executar coverage completo
    print(f"\n{'='*60}")
    print("📊 Executando Coverage Completo")
    print(f"{'='*60}")
    
    coverage_success, coverage_stdout, coverage_stderr = run_command(
        'coverage run --source="." manage.py test apps.accounts.tests.test_models apps.config.tests.test_models apps.articles.tests.test_models --keepdb',
        'Coverage - Modelos'
    )
    
    if coverage_success:
        # Gerar relatório de coverage
        run_command('coverage report', 'Relatório de Coverage')
        run_command('coverage html', 'Relatório HTML de Coverage')
    
    # Resumo final
    print(f"\n{'='*60}")
    print("📋 RESUMO FINAL")
    print(f"{'='*60}")
    
    successful_tests = sum(1 for r in results if r['success'])
    total_test_suites = len(results)
    
    print(f"📊 Total de suítes de teste: {total_test_suites}")
    print(f"✅ Suítes bem-sucedidas: {successful_tests}")
    print(f"❌ Suítes com falhas: {total_test_suites - successful_tests}")
    print(f"🧪 Total estimado de testes: {total_tests}")
    
    if coverage_success:
        print(f"📈 Relatório de coverage gerado em: htmlcov/index.html")
    
    # Detalhes das falhas
    failed_tests = [r for r in results if not r['success']]
    if failed_tests:
        print(f"\n❌ FALHAS DETECTADAS:")
        for test in failed_tests:
            print(f"  - {test['description']}")
    
    print(f"\n🏁 Execução concluída em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Retornar código de saída apropriado
    if failed_tests:
        sys.exit(1)
    else:
        print("🎉 Todos os testes passaram!")
        sys.exit(0)

if __name__ == '__main__':
    main()
