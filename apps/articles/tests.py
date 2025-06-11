from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.articles.models import Article, Category

User = get_user_model()


class CategoryModelTest(TestCase):
    """Testes para o modelo Category"""

    def setUp(self):
        self.category_data = {
            'name': 'Tecnologia',
            'slug': 'tecnologia',
            'description': 'Artigos sobre tecnologia'
        }

    def test_create_category(self):
        """Teste criação de categoria"""
        category = Category.objects.create(**self.category_data)
        self.assertEqual(category.name, 'Tecnologia')
        self.assertEqual(category.slug, 'tecnologia')
        self.assertTrue(category.is_active)

    def test_category_str_method(self):
        """Teste método __str__ da categoria"""
        category = Category.objects.create(**self.category_data)
        self.assertEqual(str(category), 'Tecnologia')


class ArticleModelTest(TestCase):
    """Testes para o modelo Article"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='author@example.com',
            username='author',
            password='authorpass123'
        )
        self.category = Category.objects.create(
            name='Tecnologia',
            slug='tecnologia'
        )
        self.article_data = {
            'title': 'Artigo de Teste',
            'slug': 'artigo-teste',
            'content': '<p>Conteúdo do artigo de teste</p>',
            'excerpt': 'Resumo do artigo',
            'status': 'published',
            'author': self.user,
            'category': self.category
        }

    def test_create_article(self):
        """Teste criação de artigo"""
        article = Article.objects.create(**self.article_data)
        self.assertEqual(article.title, 'Artigo de Teste')
        self.assertEqual(article.slug, 'artigo-teste')
        self.assertEqual(article.status, 'published')
        self.assertEqual(article.author, self.user)
        self.assertEqual(article.category, self.category)

    def test_article_str_method(self):
        """Teste método __str__ do artigo"""
        article = Article.objects.create(**self.article_data)
        self.assertEqual(str(article), 'Artigo de Teste')

    def test_article_get_absolute_url(self):
        """Teste método get_absolute_url"""
        article = Article.objects.create(**self.article_data)
        expected_url = reverse('articles:article_detail', kwargs={'slug': 'artigo-teste'})
        self.assertEqual(article.get_absolute_url(), expected_url)

    def test_article_is_published(self):
        """Teste se artigo está publicado"""
        article = Article.objects.create(**self.article_data)
        self.assertTrue(article.status == 'published')

        article.status = 'draft'
        article.save()
        self.assertFalse(article.status == 'published')


class ArticleViewsTest(TestCase):
    """Testes para as views de artigos"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='author@example.com',
            username='author',
            password='authorpass123'
        )
        self.category = Category.objects.create(
            name='Tecnologia',
            slug='tecnologia'
        )
        self.article = Article.objects.create(
            title='Artigo de Teste',
            slug='artigo-teste',
            content='<p>Conteúdo do artigo de teste</p>',
            excerpt='Resumo do artigo',
            status='published',
            author=self.user,
            category=self.category
        )

    def test_article_list_view(self):
        """Teste da listagem de artigos"""
        response = self.client.get(reverse('articles:article_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Artigo de Teste')

    def test_article_detail_view(self):
        """Teste da view de detalhes do artigo"""
        response = self.client.get(reverse('articles:article_detail', kwargs={'slug': 'artigo-teste'}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Artigo de Teste')
        self.assertContains(response, 'Conteúdo do artigo de teste')

    def test_article_detail_view_not_found(self):
        """Teste da view de detalhes com artigo inexistente"""
        response = self.client.get(reverse('articles:article_detail', kwargs={'slug': 'nao-existe'}))
        self.assertEqual(response.status_code, 404)

    def test_category_view(self):
        """Teste da view de categoria"""
        response = self.client.get(reverse('articles:category_detail', kwargs={'slug': 'tecnologia'}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tecnologia')
        self.assertContains(response, 'Artigo de Teste')

    def test_category_view_not_found(self):
        """Teste da view de categoria inexistente"""
        response = self.client.get(reverse('articles:category_detail', kwargs={'slug': 'nao-existe'}))
        self.assertEqual(response.status_code, 404)


class ArticleSearchTest(TestCase):
    """Testes para busca de artigos"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='author@example.com',
            username='author',
            password='authorpass123'
        )
        self.category = Category.objects.create(
            name='Tecnologia',
            slug='tecnologia'
        )
        self.article = Article.objects.create(
            title='Django Framework',
            slug='django-framework',
            content='<p>Django é um framework web em Python</p>',
            excerpt='Artigo sobre Django',
            status='published',
            author=self.user,
            category=self.category
        )

    def test_search_articles(self):
        """Teste busca de artigos"""
        response = self.client.get(reverse('articles:article_search'), {'q': 'Django'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Django Framework')

    def test_search_no_results(self):
        """Teste busca sem resultados"""
        response = self.client.get(reverse('articles:article_search'), {'q': 'inexistente'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nenhum resultado')
