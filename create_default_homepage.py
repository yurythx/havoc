#!/usr/bin/env python
"""
Script para criar uma homepage padrão se não existir
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.pages.models import Page
from django.contrib.auth import get_user_model

User = get_user_model()

def create_default_homepage():
    """Cria uma homepage padrão se não existir"""
    print("🏠 CRIANDO HOMEPAGE PADRÃO")
    print("=" * 50)
    
    # Verificar se já existe uma homepage
    existing_homepage = Page.objects.filter(is_homepage=True).first()
    if existing_homepage:
        print(f"✅ Homepage já existe: {existing_homepage.title}")
        return existing_homepage
    
    # Verificar se há usuário admin para criar a página
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        admin_user = User.objects.filter(is_staff=True).first()
    
    if not admin_user:
        print("❌ Nenhum usuário admin encontrado")
        print("💡 Crie um superusuário primeiro: python manage.py createsuperuser")
        return None
    
    print(f"👤 Usando usuário: {admin_user.email}")
    
    # Conteúdo da homepage
    content = """
    <div class="hero-section bg-django-green text-light py-5">
        <div class="container">
            <div class="row align-items-center">
                <div class="col-lg-8">
                    <h1 class="display-4 fw-bold">Bem-vindo ao Havoc</h1>
                    <p class="lead">Sistema moderno de gerenciamento de conteúdo com arquitetura limpa e princípios SOLID.</p>
                    <div class="mt-4">
                        <a href="/sobre/" class="btn btn-light btn-lg me-3">
                            <i class="fas fa-info-circle me-2"></i>Saiba Mais
                        </a>
                        <a href="/contato/" class="btn btn-outline-light btn-lg">
                            <i class="fas fa-envelope me-2"></i>Contato
                        </a>
                    </div>
                </div>
                <div class="col-lg-4">
                    <div class="text-center">
                        <i class="fas fa-rocket fa-8x opacity-75"></i>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="container my-5">
        <div class="row">
            <div class="col-12 text-center mb-5">
                <h2>Sistema em Funcionamento</h2>
                <p class="text-secondary">Todas as funcionalidades estão operacionais!</p>
            </div>
        </div>
        
        <div class="row g-4">
            <div class="col-md-4">
                <div class="card h-100 border-0 shadow-sm">
                    <div class="card-body text-center">
                        <div class="feature-icon mb-3">
                            <i class="fas fa-check-circle fa-3x text-success"></i>
                        </div>
                        <h5 class="card-title">App Pages</h5>
                        <p class="card-text">Sistema de páginas implementado com arquitetura limpa.</p>
                    </div>
                </div>
            </div>
            
            <div class="col-md-4">
                <div class="card h-100 border-0 shadow-sm">
                    <div class="card-body text-center">
                        <div class="feature-icon mb-3">
                            <i class="fas fa-users fa-3x text-django-green"></i>
                        </div>
                        <h5 class="card-title">App Accounts</h5>
                        <p class="card-text">Sistema completo de autenticação e gerenciamento de usuários.</p>
                    </div>
                </div>
            </div>
            
            <div class="col-md-4">
                <div class="card h-100 border-0 shadow-sm">
                    <div class="card-body text-center">
                        <div class="feature-icon mb-3">
                            <i class="fas fa-cog fa-3x text-warning"></i>
                        </div>
                        <h5 class="card-title">App Config</h5>
                        <p class="card-text">Painel administrativo para configuração do sistema.</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """
    
    try:
        # Criar a homepage
        homepage = Page.objects.create(
            title='Página Inicial - Havoc',
            slug='home',
            content=content.strip(),
            excerpt='Página inicial do sistema Havoc - Sistema moderno de gerenciamento de conteúdo',
            status='published',
            is_homepage=True,
            show_in_menu=False,
            meta_title='Havoc - Sistema de Gerenciamento de Conteúdo',
            meta_description='Sistema moderno de gerenciamento de conteúdo com arquitetura limpa e princípios SOLID',
            meta_keywords='havoc, cms, django, sistema, gerenciamento, conteúdo',
            created_by=admin_user,
            updated_by=admin_user
        )
        
        print(f"✅ Homepage criada com sucesso!")
        print(f"   - Título: {homepage.title}")
        print(f"   - Slug: {homepage.slug}")
        print(f"   - Status: {homepage.status}")
        print(f"   - Homepage: {homepage.is_homepage}")
        print(f"   - Criado por: {homepage.created_by.email}")
        
        return homepage
        
    except Exception as e:
        print(f"❌ Erro ao criar homepage: {e}")
        return None

def create_additional_pages():
    """Cria páginas adicionais se não existirem"""
    print("\n📄 CRIANDO PÁGINAS ADICIONAIS")
    print("=" * 50)
    
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        admin_user = User.objects.filter(is_staff=True).first()
    
    if not admin_user:
        print("❌ Nenhum usuário admin encontrado")
        return
    
    pages_to_create = [
        {
            'title': 'Sobre Nós',
            'slug': 'sobre',
            'content': '''
            <div class="container my-5">
                <div class="row">
                    <div class="col-lg-8 mx-auto">
                        <h1>Sobre o Havoc</h1>
                        <p class="lead">O Havoc é um sistema moderno de gerenciamento de conteúdo desenvolvido com Django.</p>
                        
                        <h3>Características</h3>
                        <ul>
                            <li>Arquitetura limpa e princípios SOLID</li>
                            <li>Sistema de autenticação completo</li>
                            <li>Painel administrativo avançado</li>
                            <li>Interface responsiva e moderna</li>
                        </ul>
                        
                        <h3>Tecnologias</h3>
                        <ul>
                            <li>Django 5.2</li>
                            <li>Bootstrap 5</li>
                            <li>FontAwesome</li>
                            <li>PostgreSQL/SQLite</li>
                        </ul>
                    </div>
                </div>
            </div>
            ''',
            'excerpt': 'Conheça mais sobre o sistema Havoc e suas funcionalidades',
            'meta_title': 'Sobre o Havoc - Sistema de Gerenciamento',
            'meta_description': 'Conheça o Havoc, sistema moderno de gerenciamento de conteúdo desenvolvido com Django'
        },
        {
            'title': 'Contato',
            'slug': 'contato',
            'content': '''
            <div class="container my-5">
                <div class="row">
                    <div class="col-lg-8 mx-auto">
                        <h1>Entre em Contato</h1>
                        <p class="lead">Tem alguma dúvida ou sugestão? Entre em contato conosco!</p>
                        
                        <div class="row mt-4">
                            <div class="col-md-6">
                                <h4>Informações</h4>
                                <p><i class="fas fa-envelope me-2"></i> contato@havoc.com</p>
                                <p><i class="fas fa-phone me-2"></i> (11) 99999-9999</p>
                                <p><i class="fas fa-map-marker-alt me-2"></i> São Paulo, SP</p>
                            </div>
                            <div class="col-md-6">
                                <h4>Suporte</h4>
                                <p>Para suporte técnico, acesse o painel administrativo ou entre em contato através dos canais oficiais.</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            ''',
            'excerpt': 'Entre em contato conosco para dúvidas e suporte',
            'meta_title': 'Contato - Havoc',
            'meta_description': 'Entre em contato com a equipe do Havoc para dúvidas e suporte técnico'
        }
    ]
    
    created_count = 0
    for page_data in pages_to_create:
        # Verificar se a página já existe
        if Page.objects.filter(slug=page_data['slug']).exists():
            print(f"⏭️  Página '{page_data['title']}' já existe")
            continue
        
        try:
            page = Page.objects.create(
                title=page_data['title'],
                slug=page_data['slug'],
                content=page_data['content'].strip(),
                excerpt=page_data['excerpt'],
                status='published',
                is_homepage=False,
                show_in_menu=True,
                menu_order=created_count + 1,
                meta_title=page_data['meta_title'],
                meta_description=page_data['meta_description'],
                created_by=admin_user,
                updated_by=admin_user
            )
            
            print(f"✅ Página criada: {page.title}")
            created_count += 1
            
        except Exception as e:
            print(f"❌ Erro ao criar página '{page_data['title']}': {e}")
    
    print(f"\n📊 Total de páginas criadas: {created_count}")

if __name__ == '__main__':
    print("🚀 INICIANDO CRIAÇÃO DE PÁGINAS PADRÃO")
    print("=" * 60)
    
    # Verificar total de páginas atual
    total_pages = Page.objects.count()
    print(f"📄 Páginas existentes: {total_pages}")
    
    # Criar homepage se não existir
    homepage = create_default_homepage()
    
    # Criar páginas adicionais
    create_additional_pages()
    
    # Verificar total final
    final_total = Page.objects.count()
    print(f"\n📊 RESUMO FINAL")
    print("=" * 30)
    print(f"📄 Páginas antes: {total_pages}")
    print(f"📄 Páginas depois: {final_total}")
    print(f"📄 Páginas criadas: {final_total - total_pages}")
    
    if homepage:
        print(f"\n🏠 Homepage disponível em: /")
        print(f"🔗 URL da homepage: {homepage.get_absolute_url()}")
    
    print("\n🎉 PROCESSO CONCLUÍDO!")
