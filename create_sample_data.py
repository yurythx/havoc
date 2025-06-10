#!/usr/bin/env python
"""
Script para criar dados de exemplo para o app articles
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.articles.models.article import Article
from apps.articles.models.category import Category
from apps.articles.models.tag import Tag
from django.utils import timezone

User = get_user_model()

def create_sample_data():
    """Cria dados de exemplo"""
    
    # Obter ou criar usuário admin
    try:
        admin_user = User.objects.get(username='admin')
        print(f"✅ Usuário admin encontrado: {admin_user.email}")
    except User.DoesNotExist:
        print("❌ Usuário admin não encontrado. Execute: python manage.py createsuperuser")
        return
    
    # Criar categorias
    categories_data = [
        {
            'name': 'Tecnologia',
            'description': 'Artigos sobre tecnologia e inovação',
            'color': '#007bff',
            'icon': 'fas fa-laptop-code'
        },
        {
            'name': 'Django',
            'description': 'Tutoriais e dicas sobre Django',
            'color': '#092e20',
            'icon': 'fab fa-python'
        },
        {
            'name': 'Frontend',
            'description': 'Desenvolvimento frontend e UI/UX',
            'color': '#fd7e14',
            'icon': 'fas fa-paint-brush'
        },
        {
            'name': 'Backend',
            'description': 'Desenvolvimento backend e APIs',
            'color': '#6f42c1',
            'icon': 'fas fa-server'
        }
    ]
    
    categories = {}
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults=cat_data
        )
        categories[cat_data['name']] = category
        status = "criada" if created else "já existe"
        print(f"📁 Categoria '{category.name}' {status}")
    
    # Criar tags
    tags_data = [
        {'name': 'Python', 'color': '#3776ab'},
        {'name': 'JavaScript', 'color': '#f7df1e'},
        {'name': 'HTML', 'color': '#e34f26'},
        {'name': 'CSS', 'color': '#1572b6'},
        {'name': 'Bootstrap', 'color': '#7952b3'},
        {'name': 'API', 'color': '#ff6b6b'},
        {'name': 'Tutorial', 'color': '#4ecdc4'},
        {'name': 'Iniciante', 'color': '#45b7d1'},
        {'name': 'Avançado', 'color': '#f39c12'},
        {'name': 'Dicas', 'color': '#27ae60'}
    ]
    
    tags = {}
    for tag_data in tags_data:
        tag, created = Tag.objects.get_or_create(
            name=tag_data['name'],
            defaults=tag_data
        )
        tags[tag_data['name']] = tag
        status = "criada" if created else "já existe"
        print(f"🏷️ Tag '{tag.name}' {status}")
    
    # Criar artigos
    articles_data = [
        {
            'title': 'Introdução ao Django: Seu Primeiro Projeto Web',
            'excerpt': 'Aprenda a criar sua primeira aplicação web com Django, o framework Python mais popular para desenvolvimento web.',
            'content': '''
<h2>O que é Django?</h2>
<p>Django é um framework web de alto nível escrito em Python que encoraja o desenvolvimento rápido e limpo. Ele segue o princípio DRY (Don't Repeat Yourself) e inclui muitas funcionalidades prontas para uso.</p>

<h2>Instalação</h2>
<p>Para instalar o Django, você pode usar o pip:</p>
<pre><code>pip install django</code></pre>

<h2>Criando seu primeiro projeto</h2>
<p>Execute o comando abaixo para criar um novo projeto Django:</p>
<pre><code>django-admin startproject meusite</code></pre>

<h2>Executando o servidor</h2>
<p>Navegue até o diretório do projeto e execute:</p>
<pre><code>python manage.py runserver</code></pre>

<p>Agora você pode acessar <code>http://127.0.0.1:8000</code> e ver sua aplicação funcionando!</p>
            ''',
            'category': 'Django',
            'tags': ['Python', 'Django', 'Tutorial', 'Iniciante'],
            'status': 'published',
            'is_featured': True
        },
        {
            'title': 'CSS Grid vs Flexbox: Quando Usar Cada Um',
            'excerpt': 'Entenda as diferenças entre CSS Grid e Flexbox e saiba quando usar cada uma dessas poderosas ferramentas de layout.',
            'content': '''
<h2>CSS Grid</h2>
<p>CSS Grid é ideal para layouts bidimensionais, onde você precisa controlar tanto linhas quanto colunas.</p>

<h3>Quando usar Grid:</h3>
<ul>
<li>Layouts complexos de página</li>
<li>Quando você precisa de controle preciso sobre linhas e colunas</li>
<li>Para criar layouts responsivos complexos</li>
</ul>

<h2>Flexbox</h2>
<p>Flexbox é perfeito para layouts unidimensionais, seja em linha ou coluna.</p>

<h3>Quando usar Flexbox:</h3>
<ul>
<li>Alinhamento de itens em uma direção</li>
<li>Distribuição de espaço entre elementos</li>
<li>Componentes pequenos e simples</li>
</ul>

<h2>Conclusão</h2>
<p>Ambas as tecnologias são complementares e podem ser usadas juntas para criar layouts modernos e responsivos.</p>
            ''',
            'category': 'Frontend',
            'tags': ['CSS', 'Frontend', 'Tutorial'],
            'status': 'published',
            'is_featured': False
        },
        {
            'title': 'Construindo APIs RESTful com Django REST Framework',
            'excerpt': 'Aprenda a criar APIs robustas e escaláveis usando Django REST Framework, a ferramenta mais popular para APIs em Django.',
            'content': '''
<h2>O que é Django REST Framework?</h2>
<p>Django REST Framework (DRF) é uma biblioteca poderosa e flexível para construir APIs web em Django.</p>

<h2>Instalação</h2>
<pre><code>pip install djangorestframework</code></pre>

<h2>Configuração Básica</h2>
<p>Adicione ao seu INSTALLED_APPS:</p>
<pre><code>INSTALLED_APPS = [
    ...
    'rest_framework',
]</code></pre>

<h2>Criando seu primeiro Serializer</h2>
<p>Serializers convertem dados complexos em tipos Python nativos:</p>
<pre><code>from rest_framework import serializers

class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'</code></pre>

<h2>ViewSets e Routers</h2>
<p>Use ViewSets para criar rapidamente um conjunto completo de views CRUD.</p>
            ''',
            'category': 'Backend',
            'tags': ['Python', 'Django', 'API', 'Avançado'],
            'status': 'published',
            'is_featured': True
        },
        {
            'title': 'Bootstrap 5: Novidades e Melhorias',
            'excerpt': 'Descubra as principais novidades do Bootstrap 5 e como migrar seus projetos da versão anterior.',
            'content': '''
<h2>Principais Novidades</h2>
<p>Bootstrap 5 trouxe várias melhorias importantes:</p>

<h3>1. Remoção do jQuery</h3>
<p>Bootstrap 5 não depende mais do jQuery, tornando-o mais leve e moderno.</p>

<h3>2. Novo Sistema de Cores</h3>
<p>Novas variáveis CSS customizáveis para cores e temas.</p>

<h3>3. Utilitários Aprimorados</h3>
<p>Mais classes utilitárias para spacing, flexbox e grid.</p>

<h2>Como Migrar</h2>
<ol>
<li>Atualize os CDNs ou arquivos locais</li>
<li>Remova dependências do jQuery se não precisar</li>
<li>Atualize classes que mudaram</li>
<li>Teste componentes JavaScript</li>
</ol>
            ''',
            'category': 'Frontend',
            'tags': ['Bootstrap', 'CSS', 'Frontend', 'Dicas'],
            'status': 'published',
            'is_featured': False
        },
        {
            'title': 'Rascunho: Artigo em Desenvolvimento',
            'excerpt': 'Este é um artigo que ainda está sendo escrito e não deve aparecer na listagem pública.',
            'content': '''
<h2>Conteúdo em desenvolvimento</h2>
<p>Este artigo ainda está sendo escrito...</p>
            ''',
            'category': 'Tecnologia',
            'tags': ['Tutorial'],
            'status': 'draft',
            'is_featured': False
        }
    ]
    
    for article_data in articles_data:
        # Verificar se artigo já existe
        if Article.objects.filter(title=article_data['title']).exists():
            print(f"📄 Artigo '{article_data['title']}' já existe")
            continue
            
        # Obter categoria
        category = categories.get(article_data['category'])
        
        # Criar artigo
        article = Article.objects.create(
            title=article_data['title'],
            excerpt=article_data['excerpt'],
            content=article_data['content'],
            category=category,
            status=article_data['status'],
            is_featured=article_data['is_featured'],
            author=admin_user,
            published_at=timezone.now() if article_data['status'] == 'published' else None
        )
        
        # Adicionar tags
        for tag_name in article_data['tags']:
            if tag_name in tags:
                article.tags.add(tags[tag_name])
        
        print(f"📄 Artigo '{article.title}' criado com sucesso")
    
    print("\n🎉 Dados de exemplo criados com sucesso!")
    print(f"📊 Total de categorias: {Category.objects.count()}")
    print(f"🏷️ Total de tags: {Tag.objects.count()}")
    print(f"📄 Total de artigos: {Article.objects.count()}")
    print(f"📄 Artigos publicados: {Article.objects.filter(status='published').count()}")

if __name__ == '__main__':
    create_sample_data()
