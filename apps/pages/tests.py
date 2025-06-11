from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.pages.models import Page

User = get_user_model()


class PageModelTest(TestCase):
    """Testes para o modelo Page"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.page_data = {
            'title': 'Página de Teste',
            'slug': 'pagina-teste',
            'content': '<p>Conteúdo de teste</p>',
            'status': 'published',
            'created_by': self.user,
            'updated_by': self.user
        }

    def test_create_page(self):
        """Teste criação de página"""
        page = Page.objects.create(**self.page_data)
        self.assertEqual(page.title, 'Página de Teste')
        self.assertEqual(page.slug, 'pagina-teste')
        self.assertEqual(page.status, 'published')
        self.assertEqual(page.created_by, self.user)

    def test_page_str_method(self):
        """Teste método __str__ da página"""
        page = Page.objects.create(**self.page_data)
        self.assertEqual(str(page), 'Página de Teste')

    def test_page_get_absolute_url(self):
        """Teste método get_absolute_url"""
        page = Page.objects.create(**self.page_data)
        expected_url = reverse('pages:page_detail', kwargs={'slug': 'pagina-teste'})
        self.assertEqual(page.get_absolute_url(), expected_url)

    def test_page_is_published(self):
        """Teste método is_published"""
        page = Page.objects.create(**self.page_data)
        self.assertTrue(page.is_published())

        page.status = 'draft'
        page.save()
        self.assertFalse(page.is_published())


class PageViewsTest(TestCase):
    """Testes para as views de páginas"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.page = Page.objects.create(
            title='Página de Teste',
            slug='pagina-teste',
            content='<p>Conteúdo de teste</p>',
            status='published',
            created_by=self.user,
            updated_by=self.user
        )

    def test_home_view(self):
        """Teste da página inicial"""
        response = self.client.get(reverse('pages:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Havoc')

    def test_about_view(self):
        """Teste da página sobre"""
        response = self.client.get(reverse('pages:about'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sobre')

    def test_contact_view(self):
        """Teste da página de contato"""
        response = self.client.get(reverse('pages:contact'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Contato')

    def test_page_detail_view(self):
        """Teste da view de detalhes da página"""
        response = self.client.get(reverse('pages:page_detail', kwargs={'slug': 'pagina-teste'}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Página de Teste')
        self.assertContains(response, 'Conteúdo de teste')

    def test_page_detail_view_not_found(self):
        """Teste da view de detalhes com página inexistente"""
        response = self.client.get(reverse('pages:page_detail', kwargs={'slug': 'nao-existe'}))
        self.assertEqual(response.status_code, 404)

    def test_page_list_view(self):
        """Teste da listagem de páginas"""
        response = self.client.get(reverse('pages:page_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Página de Teste')

    def test_search_view(self):
        """Teste da busca de páginas"""
        response = self.client.get(reverse('pages:search'), {'q': 'teste'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Página de Teste')


class StaticPagesTest(TestCase):
    """Testes para páginas estáticas"""

    def setUp(self):
        self.client = Client()

    def test_privacy_view(self):
        """Teste da página de privacidade"""
        response = self.client.get(reverse('pages:privacy'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Privacidade')

    def test_terms_view(self):
        """Teste da página de termos"""
        response = self.client.get(reverse('pages:terms'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Termos')

    def test_design_demo_view(self):
        """Teste da página de demo do design"""
        response = self.client.get(reverse('pages:design_demo'))
        self.assertEqual(response.status_code, 200)
