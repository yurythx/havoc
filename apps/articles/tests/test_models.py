"""
Testes para os modelos do app articles.
"""
import tempfile
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.articles.models import Article, Category, Tag, Comment

User = get_user_model()


class CategoryModelTest(TestCase):
    """Testes para o modelo Category."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        self.category_data = {
            'name': 'Tecnologia',
            'description': 'Artigos sobre tecnologia',
            'color': '#007bff',
            'icon': 'fas fa-laptop'
        }
    
    def test_category_creation(self):
        """Testa criação de categoria."""
        category = Category.objects.create(**self.category_data)
        
        self.assertEqual(category.name, 'Tecnologia')
        self.assertEqual(category.description, 'Artigos sobre tecnologia')
        self.assertEqual(category.color, '#007bff')
        self.assertEqual(category.icon, 'fas fa-laptop')
        self.assertTrue(category.is_active)
        self.assertEqual(category.order, 0)
        self.assertIsNotNone(category.created_at)
        self.assertIsNotNone(category.updated_at)
    
    def test_category_str_representation(self):
        """Testa representação string da categoria."""
        category = Category.objects.create(**self.category_data)
        self.assertEqual(str(category), 'Tecnologia')
    
    def test_category_slug_generation(self):
        """Testa geração automática de slug."""
        category = Category.objects.create(**self.category_data)
        self.assertEqual(category.slug, 'tecnologia')
    
    def test_category_unique_constraints(self):
        """Testa constraints únicos."""
        Category.objects.create(**self.category_data)
        
        # Nome duplicado deve falhar
        with self.assertRaises(IntegrityError):
            Category.objects.create(**self.category_data)
    
    def test_category_hierarchy(self):
        """Testa hierarquia de categorias."""
        parent = Category.objects.create(name='Tecnologia')
        child = Category.objects.create(
            name='Programação',
            parent=parent
        )
        
        self.assertEqual(child.parent, parent)
        self.assertTrue(parent.has_children)
        self.assertFalse(child.has_children)
        
        children = parent.get_children()
        self.assertIn(child, children)
    
    def test_category_breadcrumbs(self):
        """Testa geração de breadcrumbs."""
        grandparent = Category.objects.create(name='Tecnologia')
        parent = Category.objects.create(name='Programação', parent=grandparent)
        child = Category.objects.create(name='Python', parent=parent)
        
        breadcrumbs = child.get_breadcrumbs()
        self.assertEqual(len(breadcrumbs), 3)
        self.assertEqual(breadcrumbs[0], grandparent)
        self.assertEqual(breadcrumbs[1], parent)
        self.assertEqual(breadcrumbs[2], child)
    
    def test_category_seo_properties(self):
        """Testa propriedades SEO."""
        category = Category.objects.create(
            name='Tecnologia',
            description='Artigos sobre tecnologia',
            meta_title='Tech Articles',
            meta_description='Best tech articles'
        )
        
        self.assertEqual(category.seo_title, 'Tech Articles')
        self.assertEqual(category.seo_description, 'Best tech articles')
        
        # Testa fallback
        category_no_meta = Category.objects.create(
            name='Ciência',
            description='Artigos científicos'
        )
        
        self.assertEqual(category_no_meta.seo_title, 'Ciência')
        self.assertEqual(category_no_meta.seo_description, 'Artigos científicos')


class TagModelTest(TestCase):
    """Testes para o modelo Tag."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        self.tag_data = {
            'name': 'Python',
            'description': 'Linguagem de programação Python',
            'color': '#3776ab'
        }
    
    def test_tag_creation(self):
        """Testa criação de tag."""
        tag = Tag.objects.create(**self.tag_data)
        
        self.assertEqual(tag.name, 'Python')
        self.assertEqual(tag.description, 'Linguagem de programação Python')
        self.assertEqual(tag.color, '#3776ab')
        self.assertFalse(tag.is_featured)
        self.assertIsNotNone(tag.created_at)
        self.assertIsNotNone(tag.updated_at)
    
    def test_tag_str_representation(self):
        """Testa representação string da tag."""
        tag = Tag.objects.create(**self.tag_data)
        self.assertEqual(str(tag), 'Python')
    
    def test_tag_slug_generation(self):
        """Testa geração automática de slug."""
        tag = Tag.objects.create(**self.tag_data)
        self.assertEqual(tag.slug, 'python')
    
    def test_tag_unique_constraints(self):
        """Testa constraints únicos."""
        Tag.objects.create(**self.tag_data)
        
        # Nome duplicado deve falhar
        with self.assertRaises(IntegrityError):
            Tag.objects.create(**self.tag_data)
    
    def test_tag_seo_properties(self):
        """Testa propriedades SEO."""
        tag = Tag.objects.create(
            name='Django',
            description='Framework web Django',
            meta_title='Django Articles',
            meta_description='Best Django tutorials'
        )
        
        self.assertEqual(tag.seo_title, 'Django Articles')
        self.assertEqual(tag.seo_description, 'Best Django tutorials')
        
        # Testa fallback
        tag_no_meta = Tag.objects.create(name='Flask')
        
        self.assertEqual(tag_no_meta.seo_title, 'Artigos sobre Flask')
        self.assertEqual(tag_no_meta.seo_description, 'Todos os artigos relacionados à tag Flask')


class ArticleModelTest(TestCase):
    """Testes para o modelo Article."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        self.user = User.objects.create_user(
            username='author',
            email='author@example.com',
            password='authorpass123'
        )
        
        self.category = Category.objects.create(
            name='Tecnologia',
            description='Artigos sobre tecnologia'
        )
        
        self.tag = Tag.objects.create(
            name='Python',
            description='Linguagem Python'
        )
        
        self.article_data = {
            'title': 'Introdução ao Python',
            'excerpt': 'Um guia completo para iniciantes em Python',
            'content': 'Python é uma linguagem de programação...',
            'author': self.user,
            'category': self.category,
            'status': 'draft'
        }
    
    def test_article_creation(self):
        """Testa criação de artigo."""
        article = Article.objects.create(**self.article_data)
        
        self.assertEqual(article.title, 'Introdução ao Python')
        self.assertEqual(article.excerpt, 'Um guia completo para iniciantes em Python')
        self.assertEqual(article.content, 'Python é uma linguagem de programação...')
        self.assertEqual(article.author, self.user)
        self.assertEqual(article.category, self.category)
        self.assertEqual(article.status, 'draft')
        self.assertFalse(article.is_featured)
        self.assertTrue(article.allow_comments)
        self.assertEqual(article.view_count, 0)
        self.assertIsNotNone(article.created_at)
        self.assertIsNotNone(article.updated_at)
    
    def test_article_str_representation(self):
        """Testa representação string do artigo."""
        article = Article.objects.create(**self.article_data)
        self.assertEqual(str(article), 'Introdução ao Python')
    
    def test_article_slug_generation(self):
        """Testa geração automática de slug."""
        article = Article.objects.create(**self.article_data)
        self.assertEqual(article.slug, 'introducao-ao-python')
    
    def test_article_reading_time_calculation(self):
        """Testa cálculo do tempo de leitura."""
        # Conteúdo com aproximadamente 400 palavras (2 minutos de leitura)
        content = ' '.join(['palavra'] * 400)
        
        article = Article.objects.create(
            title='Teste',
            excerpt='Teste',
            content=content,
            author=self.user
        )
        
        self.assertEqual(article.reading_time, 2)
    
    def test_article_published_at_auto_set(self):
        """Testa definição automática de published_at."""
        article = Article.objects.create(**self.article_data)
        
        # Inicialmente não deve ter published_at
        self.assertIsNone(article.published_at)
        
        # Ao mudar status para published, deve definir published_at
        article.status = 'published'
        article.save()
        
        self.assertIsNotNone(article.published_at)
    
    def test_article_is_published_property(self):
        """Testa propriedade is_published."""
        article = Article.objects.create(**self.article_data)
        
        # Draft não está publicado
        self.assertFalse(article.is_published)
        
        # Published com data está publicado
        article.status = 'published'
        article.published_at = timezone.now()
        article.save()
        
        self.assertTrue(article.is_published)
    
    def test_article_seo_properties(self):
        """Testa propriedades SEO."""
        article = Article.objects.create(
            title='Python Tutorial',
            excerpt='Learn Python basics',
            content='Content here',
            meta_title='Best Python Tutorial',
            meta_description='Complete Python guide',
            author=self.user
        )
        
        self.assertEqual(article.seo_title, 'Best Python Tutorial')
        self.assertEqual(article.seo_description, 'Complete Python guide')
        
        # Testa fallback
        article_no_meta = Article.objects.create(
            title='Django Tutorial',
            excerpt='Learn Django',
            content='Content',
            author=self.user
        )
        
        self.assertEqual(article_no_meta.seo_title, 'Django Tutorial')
        self.assertEqual(article_no_meta.seo_description, 'Learn Django')
    
    def test_article_tags_relationship(self):
        """Testa relacionamento many-to-many com tags."""
        article = Article.objects.create(**self.article_data)
        
        # Adiciona tags
        article.tags.add(self.tag)
        
        self.assertIn(self.tag, article.tags.all())
        self.assertIn(article, self.tag.articles.all())
    
    def test_article_contributors_relationship(self):
        """Testa relacionamento many-to-many com colaboradores."""
        contributor = User.objects.create_user(
            username='contributor',
            email='contributor@example.com',
            password='pass123'
        )
        
        article = Article.objects.create(**self.article_data)
        article.contributors.add(contributor)
        
        self.assertIn(contributor, article.contributors.all())
        self.assertIn(article, contributor.contributed_articles.all())
    
    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_article_featured_image(self):
        """Testa upload de imagem destacada."""
        # Criar arquivo de imagem fake
        image_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde'
        
        uploaded_file = SimpleUploadedFile(
            name='test_image.png',
            content=image_content,
            content_type='image/png'
        )
        
        article = Article.objects.create(
            title='Artigo com Imagem',
            excerpt='Teste',
            content='Conteúdo',
            featured_image=uploaded_file,
            featured_image_alt='Imagem de teste',
            author=self.user
        )
        
        self.assertTrue(article.featured_image)
        self.assertIn('articles/images/', article.featured_image.name)
        self.assertEqual(article.featured_image_alt, 'Imagem de teste')
