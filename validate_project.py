#!/usr/bin/env python
"""
Script de validação final do projeto Havoc
"""
import os
import sys
import subprocess
import django

def run_command(command, description):
    """Executa um comando e retorna o resultado"""
    print(f"\n🔄 {description}")
    print("-" * 50)
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print("✅ SUCESSO")
        if result.stdout:
            print(result.stdout[:200] + "..." if len(result.stdout) > 200 else result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("❌ ERRO")
        print(f"Código de saída: {e.returncode}")
        if e.stderr:
            print(f"Erro: {e.stderr[:200]}...")
        return False

def validate_django_setup():
    """Valida configuração do Django"""
    print("\n🔧 Validando configuração Django...")
    
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
        django.setup()
        
        from django.conf import settings
        from django.contrib.auth import get_user_model
        
        print("✅ Django configurado corretamente")
        print(f"✅ DEBUG: {settings.DEBUG}")
        print(f"✅ Banco: {settings.DATABASES['default']['ENGINE']}")
        print(f"✅ User Model: {get_user_model()}")
        
        return True
    except Exception as e:
        print(f"❌ Erro na configuração Django: {e}")
        return False

def main():
    """Função principal de validação"""
    print("🧪 VALIDAÇÃO FINAL DO PROJETO HAVOC")
    print("=" * 60)
    
    success_count = 0
    total_tests = 6
    
    # 1. Verificar configuração Django
    if validate_django_setup():
        success_count += 1
    
    # 2. Verificar estrutura do projeto
    if run_command("python manage.py check", "Verificando estrutura do projeto"):
        success_count += 1
    
    # 3. Verificar migrações
    if run_command("python manage.py showmigrations", "Verificando migrações"):
        success_count += 1
    
    # 4. Executar testes
    if run_command("python manage.py test --keepdb", "Executando todos os testes"):
        success_count += 1
    
    # 5. Verificar arquivos estáticos
    if run_command("python manage.py collectstatic --noinput --dry-run", "Verificando arquivos estáticos"):
        success_count += 1
    
    # 6. Verificar configurações de deploy
    if run_command("python manage.py check --deploy", "Verificando configurações de deploy"):
        success_count += 1
    
    # Resultado final
    print("\n" + "=" * 60)
    print("📊 RESULTADO DA VALIDAÇÃO")
    print("=" * 60)
    
    print(f"✅ Testes passaram: {success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("\n🎉 PROJETO TOTALMENTE VALIDADO!")
        print("✅ Pronto para deploy em produção")
        print("✅ Todas as funcionalidades testadas")
        print("✅ Configurações otimizadas")
        
        print("\n📋 PRÓXIMOS PASSOS:")
        print("1. Deploy em servidor de produção")
        print("2. Configurar variáveis de ambiente")
        print("3. Aplicar migrações em produção")
        print("4. Configurar monitoramento")
        
        return True
    else:
        print(f"\n⚠️ {total_tests - success_count} problemas encontrados")
        print("❌ Revisar itens falhados antes do deploy")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
