#!/usr/bin/env python
"""
Script para limpar duplicações no arquivo .env e aplicar configuração de banco
"""

import os
import re

def clean_env_file():
    """Limpa duplicações no arquivo .env"""
    
    if not os.path.exists('.env'):
        print("Arquivo .env não encontrado")
        return
    
    print("🧹 Limpando arquivo .env...")
    
    # Ler arquivo atual
    with open('.env', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Variáveis de banco que devem ser removidas para evitar duplicação
    db_vars = {
        'DB_ENGINE', 'DB_NAME', 'DB_USER', 'DB_PASSWORD', 
        'DB_HOST', 'DB_PORT', 'DATABASE_URL'
    }
    
    # Filtrar linhas
    cleaned_lines = []
    found_vars = set()

    for line in lines:
        line_stripped = line.strip()

        # Pular comentários sobre configurações de banco duplicadas
        if 'Configurações de Banco de Dados atualizadas automaticamente' in line:
            continue

        # Verificar se é uma variável de banco
        if '=' in line_stripped and not line_stripped.startswith('#'):
            var_name = line_stripped.split('=')[0].strip()
            if var_name in db_vars:
                # Só manter a primeira ocorrência
                if var_name not in found_vars:
                    found_vars.add(var_name)
                    cleaned_lines.append(line)
                continue

        # Manter outras linhas
        cleaned_lines.append(line)

    # Remover linhas vazias duplicadas no final
    while cleaned_lines and cleaned_lines[-1].strip() == '':
        cleaned_lines.pop()
    
    # Escrever arquivo limpo
    with open('.env', 'w', encoding='utf-8') as f:
        f.writelines(cleaned_lines)
    
    print("✅ Arquivo .env limpo com sucesso!")

def apply_db_config():
    """Aplica configuração de banco via Django"""
    import django
    import os
    
    # Configurar Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    django.setup()
    
    from apps.config.models.configuration_models import DatabaseConfiguration
    
    print("\n🔧 Aplicando configuração de banco...")
    
    # Buscar configuração padrão
    default_config = DatabaseConfiguration.get_default()
    if not default_config:
        print("❌ Nenhuma configuração padrão encontrada")
        return
    
    print(f"Aplicando configuração: {default_config.name}")
    
    # Aplicar configuração
    success, message = default_config.update_env_file()
    if success:
        print(f"✅ {message}")
    else:
        print(f"❌ {message}")

if __name__ == '__main__':
    clean_env_file()
    apply_db_config()
    print("\n🎉 Processo concluído!")
