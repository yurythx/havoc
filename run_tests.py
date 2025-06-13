#!/usr/bin/env python
"""
Script para executar todos os testes do projeto Havoc com coverage.
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_command(command, description):
    """Executa um comando e exibe o resultado."""
    print(f"\n{'='*60}")
    print(f"🔄 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar: {command}")
        print(f"Código de saída: {e.returncode}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False

def main():
    """Função principal."""
    parser = argparse.ArgumentParser(description='Executa testes do projeto Havoc')
    parser.add_argument('--app', help='Executar testes apenas para um app específico')
    parser.add_argument('--coverage', action='store_true', help='Executar com coverage')
    parser.add_argument('--html', action='store_true', help='Gerar relatório HTML do coverage')
    parser.add_argument('--verbose', '-v', action='store_true', help='Modo verboso')
    parser.add_argument('--failfast', action='store_true', help='Parar no primeiro erro')
    parser.add_argument('--parallel', action='store_true', help='Executar testes em paralelo')

    args = parser.parse_args()

    # Verificar se estamos no diretório correto
    if not Path('manage.py').exists():
        print("❌ Erro: manage.py não encontrado. Execute este script no diretório raiz do projeto.")
        sys.exit(1)

    # Configurar variável de ambiente do Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    
    print("🧪 EXECUTANDO TESTES DO PROJETO HAVOC")
    print("=" * 60)
    
    # Configurar comando base
    base_cmd = "python manage.py test"
    
    # Adicionar opções
    if args.verbose:
        base_cmd += " -v 2"
    
    if args.failfast:
        base_cmd += " --failfast"
    
    if args.parallel:
        base_cmd += " --parallel"
    
    # Definir quais testes executar
    if args.app:
        test_targets = [f"apps.{args.app}.tests"]
        print(f"🎯 Executando testes apenas para o app: {args.app}")
    else:
        test_targets = [
            "apps.accounts.tests",
            "apps.config.tests", 
            "apps.articles.tests",
            "tests"  # Testes de integração
        ]
        print("🎯 Executando todos os testes")
    
    success = True
    
    if args.coverage:
        print("\n📊 EXECUTANDO COM COVERAGE")
        
        # Limpar dados de coverage anteriores
        run_command("coverage erase", "Limpando dados de coverage anteriores")
        
        # Executar testes com coverage
        for target in test_targets:
            cmd = f"coverage run --append -m django test {target}"
            if args.verbose:
                cmd += " -v 2"
            if args.failfast:
                cmd += " --failfast"
            if args.parallel:
                cmd += " --parallel"
            
            if not run_command(cmd, f"Executando testes com coverage: {target}"):
                success = False
                if args.failfast:
                    break
        
        if success:
            # Gerar relatório de coverage
            print("\n📈 GERANDO RELATÓRIO DE COVERAGE")
            run_command("coverage report", "Relatório de coverage no terminal")
            
            if args.html:
                run_command("coverage html", "Gerando relatório HTML de coverage")
                print("\n🌐 Relatório HTML gerado em: htmlcov/index.html")
            
            # Gerar XML para CI/CD
            run_command("coverage xml", "Gerando relatório XML de coverage")
    
    else:
        print("\n🧪 EXECUTANDO TESTES SEM COVERAGE")
        
        # Executar testes sem coverage
        for target in test_targets:
            cmd = f"{base_cmd} {target}"
            
            if not run_command(cmd, f"Executando testes: {target}"):
                success = False
                if args.failfast:
                    break
    
    # Resumo final
    print("\n" + "="*60)
    if success:
        print("✅ TODOS OS TESTES EXECUTADOS COM SUCESSO!")
        
        if args.coverage:
            print("\n📊 RESUMO DE COVERAGE:")
            subprocess.run("coverage report --show-missing", shell=True)
            
            if args.html:
                print(f"\n🌐 Relatório HTML disponível em: {Path.cwd()}/htmlcov/index.html")
    else:
        print("❌ ALGUNS TESTES FALHARAM!")
        sys.exit(1)
    
    print("="*60)

if __name__ == "__main__":
    main()
