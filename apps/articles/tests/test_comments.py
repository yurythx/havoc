"""
Testes para o sistema de comentários dos artigos.
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from unittest.mock import patch

from apps.articles.models.article import Article
from apps.articles.models.category import Category
from apps.articles.models.comment import Comment
from apps.articles.forms import CommentForm, ReplyForm

User = get_user_model()


class CommentModelTest(TestCase):
    """Testes para o modelo Comment."""

    def setUp(self):
        """Configuração inicial para os testes."""
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            is_verified=True
        )
        
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )
        
        self.article = Article.objects.create(
            title='Test Article',
            slug='test-article',
            excerpt='Test excerpt',
            content='Test content',
            author=self.user,
            category=self.category,
            status='published',
            allow_comments=True
        )

    def test_create_comment(self):
        """Testa criação de comentário."""
        comment = Comment.objects.create(
            article=self.article,
            user=self.user,
            name='Test User',
            email='test@example.com',
            content='Test comment content'
        )
        
        self.assertEqual(comment.article, self.article)
        self.assertEqual(comment.user, self.user)
        self.assertEqual(comment.name, 'Test User')
        self.assertEqual(comment.content, 'Test comment content')
        self.assertFalse(comment.is_approved)
        self.assertFalse(comment.is_spam)

    def test_create_anonymous_comment(self):
        """Testa criação de comentário anônimo."""
        comment = Comment.objects.create(
            article=self.article,
            name='Anonymous User',
            email='anonymous@example.com',
            content='Anonymous comment',
            website='https://example.com'
        )
        
        self.assertIsNone(comment.user)
        self.assertEqual(comment.name, 'Anonymous User')
        self.assertEqual(comment.website, 'https://example.com')

    def test_create_reply(self):
        """Testa criação de resposta a comentário."""
        parent_comment = Comment.objects.create(
            article=self.article,
            user=self.user,
            name='Parent User',
            email='parent@example.com',
            content='Parent comment'
        )
        
        reply = Comment.objects.create(
            article=self.article,
            parent=parent_comment,
            name='Reply User',
            email='reply@example.com',
            content='Reply content'
        )
        
        self.assertEqual(reply.parent, parent_comment)
        self.assertTrue(reply.is_reply)
        self.assertEqual(parent_comment.replies.count(), 1)

    def test_comment_str(self):
        """Testa representação string do comentário."""
        comment = Comment.objects.create(
            article=self.article,
            name='Test User',
            email='test@example.com',
            content='Test content'
        )
        
        expected = f"Comentário de Test User em {self.article.title}"
        self.assertEqual(str(comment), expected)

    def test_comment_save_auto_fill(self):
        """Testa preenchimento automático de dados do usuário."""
        comment = Comment(
            article=self.article,
            user=self.user,
            content='Test content'
        )
        comment.save()
        
        self.assertEqual(comment.name, self.user.username)
        self.assertEqual(comment.email, self.user.email)

    def test_approve_comment(self):
        """Testa aprovação de comentário."""
        comment = Comment.objects.create(
            article=self.article,
            name='Test User',
            email='test@example.com',
            content='Test content'
        )
        
        self.assertFalse(comment.is_approved)
        self.assertIsNone(comment.approved_at)
        
        comment.approve()
        
        self.assertTrue(comment.is_approved)
        self.assertIsNotNone(comment.approved_at)

    def test_mark_as_spam(self):
        """Testa marcação como spam."""
        comment = Comment.objects.create(
            article=self.article,
            name='Test User',
            email='test@example.com',
            content='Test content',
            is_approved=True
        )
        
        comment.mark_as_spam()
        
        self.assertTrue(comment.is_spam)
        self.assertFalse(comment.is_approved)

    def test_get_replies(self):
        """Testa obtenção de respostas aprovadas."""
        parent_comment = Comment.objects.create(
            article=self.article,
            name='Parent User',
            email='parent@example.com',
            content='Parent comment',
            is_approved=True
        )
        
        # Resposta aprovada
        approved_reply = Comment.objects.create(
            article=self.article,
            parent=parent_comment,
            name='Approved Reply',
            email='approved@example.com',
            content='Approved reply',
            is_approved=True
        )
        
        # Resposta não aprovada
        Comment.objects.create(
            article=self.article,
            parent=parent_comment,
            name='Pending Reply',
            email='pending@example.com',
            content='Pending reply',
            is_approved=False
        )
        
        replies = parent_comment.get_replies()
        self.assertEqual(replies.count(), 1)
        self.assertEqual(replies.first(), approved_reply)

    def test_reply_count(self):
        """Testa contagem de respostas."""
        parent_comment = Comment.objects.create(
            article=self.article,
            name='Parent User',
            email='parent@example.com',
            content='Parent comment'
        )
        
        # Criar 3 respostas aprovadas
        for i in range(3):
            Comment.objects.create(
                article=self.article,
                parent=parent_comment,
                name=f'Reply User {i}',
                email=f'reply{i}@example.com',
                content=f'Reply {i}',
                is_approved=True
            )
        
        # Criar 1 resposta não aprovada
        Comment.objects.create(
            article=self.article,
            parent=parent_comment,
            name='Pending Reply',
            email='pending@example.com',
            content='Pending reply',
            is_approved=False
        )
        
        self.assertEqual(parent_comment.reply_count, 3)

    def test_author_name_property(self):
        """Testa propriedade author_name."""
        # Usuário registrado com nome completo
        user_with_name = User.objects.create_user(
            email='fullname@example.com',
            username='fullnameuser',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
        
        comment_with_user = Comment.objects.create(
            article=self.article,
            user=user_with_name,
            content='Test content'
        )
        
        self.assertEqual(comment_with_user.author_name, 'John Doe')
        
        # Usuário anônimo
        anonymous_comment = Comment.objects.create(
            article=self.article,
            name='Anonymous User',
            email='anon@example.com',
            content='Anonymous content'
        )
        
        self.assertEqual(anonymous_comment.author_name, 'Anonymous User')

    def test_can_be_replied(self):
        """Testa se comentário pode receber respostas."""
        # Comentário aprovado em artigo que permite comentários
        approved_comment = Comment.objects.create(
            article=self.article,
            name='Test User',
            email='test@example.com',
            content='Test content',
            is_approved=True
        )
        
        self.assertTrue(approved_comment.can_be_replied)
        
        # Comentário não aprovado
        pending_comment = Comment.objects.create(
            article=self.article,
            name='Pending User',
            email='pending@example.com',
            content='Pending content',
            is_approved=False
        )
        
        self.assertFalse(pending_comment.can_be_replied)
        
        # Comentário spam
        spam_comment = Comment.objects.create(
            article=self.article,
            name='Spam User',
            email='spam@example.com',
            content='Spam content',
            is_spam=True
        )
        
        self.assertFalse(spam_comment.can_be_replied)


class CommentFormTest(TestCase):
    """Testes para formulários de comentários."""

    def setUp(self):
        """Configuração inicial para os testes."""
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            is_verified=True
        )
        
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )
        
        self.article = Article.objects.create(
            title='Test Article',
            slug='test-article',
            excerpt='Test excerpt',
            content='Test content',
            author=self.user,
            category=self.category,
            status='published',
            allow_comments=True
        )

    def test_comment_form_valid_data(self):
        """Testa formulário de comentário com dados válidos."""
        form_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'website': 'https://example.com',
            'content': 'This is a valid comment content.',
            'website_url': ''  # Honeypot
        }
        
        form = CommentForm(data=form_data, article=self.article)
        self.assertTrue(form.is_valid())

    def test_comment_form_honeypot_spam(self):
        """Testa detecção de spam via honeypot."""
        form_data = {
            'name': 'Spam User',
            'email': 'spam@example.com',
            'content': 'Spam content',
            'website_url': 'http://spam.com'  # Honeypot preenchido
        }
        
        form = CommentForm(data=form_data, article=self.article)
        self.assertFalse(form.is_valid())
        self.assertIn('website_url', form.errors)

    def test_comment_form_short_name(self):
        """Testa validação de nome muito curto."""
        form_data = {
            'name': 'A',  # Muito curto
            'email': 'test@example.com',
            'content': 'Valid content here.',
            'website_url': ''
        }
        
        form = CommentForm(data=form_data, article=self.article)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_comment_form_numeric_name(self):
        """Testa validação de nome apenas numérico."""
        form_data = {
            'name': '12345',  # Apenas números
            'email': 'test@example.com',
            'content': 'Valid content here.',
            'website_url': ''
        }
        
        form = CommentForm(data=form_data, article=self.article)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_comment_form_suspicious_email(self):
        """Testa validação de email suspeito."""
        form_data = {
            'name': 'Test User',
            'email': 'test@tempmail.org',  # Domínio suspeito
            'content': 'Valid content here.',
            'website_url': ''
        }
        
        form = CommentForm(data=form_data, article=self.article)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_comment_form_short_content(self):
        """Testa validação de conteúdo muito curto."""
        form_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'content': 'Short',  # Muito curto
            'website_url': ''
        }
        
        form = CommentForm(data=form_data, article=self.article)
        self.assertFalse(form.is_valid())
        self.assertIn('content', form.errors)

    def test_comment_form_long_content(self):
        """Testa validação de conteúdo muito longo."""
        form_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'content': 'A' * 2001,  # Muito longo
            'website_url': ''
        }
        
        form = CommentForm(data=form_data, article=self.article)
        self.assertFalse(form.is_valid())
        self.assertIn('content', form.errors)

    def test_comment_form_spam_content(self):
        """Testa detecção de conteúdo spam."""
        spam_contents = [
            'Check out this amazing casino http://spam.com',
            'Buy viagra now!',
            'AMAZINGOFFER',  # 8+ caracteres maiúsculos
            'aaaaaaaaaa'  # Caracteres repetidos
        ]
        
        for spam_content in spam_contents:
            with self.subTest(content=spam_content):
                form_data = {
                    'name': 'Test User',
                    'email': 'test@example.com',
                    'content': spam_content,
                    'website_url': ''
                }
                
                form = CommentForm(data=form_data, article=self.article)
                self.assertFalse(form.is_valid())
                self.assertIn('content', form.errors)

    def test_comment_form_authenticated_user(self):
        """Testa formulário para usuário autenticado."""
        form = CommentForm(user=self.user, article=self.article)
        
        # Campos devem ser preenchidos automaticamente
        self.assertEqual(form.fields['name'].initial, self.user.username)
        self.assertEqual(form.fields['email'].initial, self.user.email)
        
        # Campos devem ser readonly
        self.assertTrue(form.fields['name'].widget.attrs.get('readonly'))
        self.assertTrue(form.fields['email'].widget.attrs.get('readonly'))

    def test_comment_form_save_authenticated(self):
        """Testa salvamento de comentário de usuário autenticado."""
        form_data = {
            'name': self.user.username,  # Usar o nome do usuário
            'email': self.user.email,    # Usar o email do usuário
            'content': 'Este é um comentário válido de usuário autenticado.',
            'website_url': ''
        }

        # Mock usuário verificado
        self.user.is_verified = True
        self.user.save()

        form = CommentForm(data=form_data, user=self.user, article=self.article)
        self.assertTrue(form.is_valid())

        comment = form.save()

        self.assertEqual(comment.user, self.user)
        self.assertEqual(comment.article, self.article)
        self.assertTrue(comment.is_approved)  # Usuário verificado = aprovação automática

    def test_reply_form(self):
        """Testa formulário de resposta."""
        parent_comment = Comment.objects.create(
            article=self.article,
            name='Parent User',
            email='parent@example.com',
            content='Parent comment',
            is_approved=True
        )
        
        form_data = {
            'name': 'Reply User',
            'email': 'reply@example.com',
            'content': 'This is a reply to the parent comment.'
        }
        
        form = ReplyForm(data=form_data, article=self.article, parent=parent_comment)
        self.assertTrue(form.is_valid())
        
        reply = form.save()
        
        self.assertEqual(reply.parent, parent_comment)
        self.assertEqual(reply.article, self.article)
        self.assertFalse(reply.is_approved)  # Usuário não verificado = moderação


class CommentViewTest(TestCase):
    """Testes para views de comentários."""

    def setUp(self):
        """Configuração inicial para os testes."""
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            is_verified=True
        )

        self.staff_user = User.objects.create_user(
            email='staff@example.com',
            username='staffuser',
            password='testpass123',
            is_staff=True
        )

        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )

        self.article = Article.objects.create(
            title='Test Article',
            slug='test-article',
            excerpt='Test excerpt',
            content='Test content',
            author=self.user,
            category=self.category,
            status='published',
            allow_comments=True
        )

    def test_add_comment_get_redirect(self):
        """Testa redirecionamento em GET para add_comment."""
        url = reverse('articles:add_comment', kwargs={'slug': self.article.slug})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('articles:article_detail', kwargs={'slug': self.article.slug}))

    def test_add_comment_post_valid(self):
        """Testa adição de comentário válido."""
        url = reverse('articles:add_comment', kwargs={'slug': self.article.slug})
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'website': 'https://example.com',
            'content': 'This is a valid comment content.',
            'website_url': ''
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Comment.objects.filter(content='This is a valid comment content.').exists())

    def test_add_comment_post_invalid(self):
        """Testa adição de comentário inválido."""
        url = reverse('articles:add_comment', kwargs={'slug': self.article.slug})
        data = {
            'name': '',  # Nome vazio
            'email': 'invalid-email',  # Email inválido
            'content': 'Short',  # Conteúdo muito curto
            'website_url': ''
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Comment.objects.filter(content='Short').exists())

    def test_add_comment_ajax_valid(self):
        """Testa adição de comentário via AJAX."""
        url = reverse('articles:add_comment', kwargs={'slug': self.article.slug})
        data = {
            'name': 'AJAX User',
            'email': 'ajax@example.com',
            'content': 'This is an AJAX comment.',
            'website_url': ''
        }

        response = self.client.post(
            url,
            data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

        json_response = response.json()
        self.assertTrue(json_response['success'])
        self.assertIn('message', json_response)

    def test_add_comment_ajax_invalid(self):
        """Testa adição de comentário inválido via AJAX."""
        url = reverse('articles:add_comment', kwargs={'slug': self.article.slug})
        data = {
            'name': '',
            'email': 'invalid',
            'content': '',
            'website_url': ''
        }

        response = self.client.post(
            url,
            data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertFalse(json_response['success'])
        self.assertIn('errors', json_response)

    def test_add_comment_comments_disabled(self):
        """Testa adição de comentário em artigo com comentários desabilitados."""
        self.article.allow_comments = False
        self.article.save()

        url = reverse('articles:add_comment', kwargs={'slug': self.article.slug})
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'content': 'This should not be allowed.',
            'website_url': ''
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Comment.objects.filter(content='This should not be allowed.').exists())

    def test_add_reply_valid(self):
        """Testa adição de resposta válida."""
        parent_comment = Comment.objects.create(
            article=self.article,
            name='Parent User',
            email='parent@example.com',
            content='Parent comment',
            is_approved=True
        )

        url = reverse('articles:add_reply', kwargs={
            'slug': self.article.slug,
            'comment_id': parent_comment.id
        })
        data = {
            'name': 'Reply User',
            'email': 'reply@example.com',
            'content': 'This is a reply to the parent comment.'
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Comment.objects.filter(
            parent=parent_comment,
            content='This is a reply to the parent comment.'
        ).exists())

    def test_add_reply_to_unapproved_comment(self):
        """Testa adição de resposta a comentário não aprovado."""
        parent_comment = Comment.objects.create(
            article=self.article,
            name='Parent User',
            email='parent@example.com',
            content='Unapproved parent comment',
            is_approved=False
        )

        url = reverse('articles:add_reply', kwargs={
            'slug': self.article.slug,
            'comment_id': parent_comment.id
        })
        data = {
            'name': 'Reply User',
            'email': 'reply@example.com',
            'content': 'This should not be allowed.'
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Comment.objects.filter(
            parent=parent_comment,
            content='This should not be allowed.'
        ).exists())

    def test_comment_list_view(self):
        """Testa visualização da lista de comentários."""
        # Criar alguns comentários
        for i in range(3):
            Comment.objects.create(
                article=self.article,
                name=f'User {i}',
                email=f'user{i}@example.com',
                content=f'Comment {i}',
                is_approved=True
            )

        url = reverse('articles:comment_list', kwargs={'slug': self.article.slug})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Comment 0')
        self.assertContains(response, 'Comment 1')
        self.assertContains(response, 'Comment 2')

    def test_comment_list_ajax(self):
        """Testa lista de comentários via AJAX."""
        Comment.objects.create(
            article=self.article,
            name='AJAX User',
            email='ajax@example.com',
            content='AJAX comment',
            is_approved=True
        )

        url = reverse('articles:comment_list', kwargs={'slug': self.article.slug})
        response = self.client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

        json_response = response.json()
        self.assertIn('comments', json_response)
        self.assertIn('total_comments', json_response)

    def test_moderate_comments_staff_required(self):
        """Testa que moderação requer staff."""
        url = reverse('articles:moderate_comments')

        # Usuário não autenticado
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        # Usuário comum
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        # Staff
        self.client.login(email='staff@example.com', password='testpass123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_moderate_comment_action_approve(self):
        """Testa aprovação de comentário via moderação."""
        comment = Comment.objects.create(
            article=self.article,
            name='Test User',
            email='test@example.com',
            content='Test comment',
            is_approved=False
        )

        self.client.login(email='staff@example.com', password='testpass123')

        url = reverse('articles:moderate_comment_action', kwargs={'comment_id': comment.id})
        response = self.client.post(url, {'action': 'approve'})

        self.assertEqual(response.status_code, 302)

        comment.refresh_from_db()
        self.assertTrue(comment.is_approved)
        self.assertIsNotNone(comment.approved_at)

    def test_moderate_comment_action_spam(self):
        """Testa marcação como spam via moderação."""
        comment = Comment.objects.create(
            article=self.article,
            name='Spam User',
            email='spam@example.com',
            content='Spam comment',
            is_approved=True
        )

        self.client.login(email='staff@example.com', password='testpass123')

        url = reverse('articles:moderate_comment_action', kwargs={'comment_id': comment.id})
        response = self.client.post(url, {'action': 'spam'})

        self.assertEqual(response.status_code, 302)

        comment.refresh_from_db()
        self.assertTrue(comment.is_spam)
        self.assertFalse(comment.is_approved)

    def test_moderate_comment_action_delete(self):
        """Testa exclusão de comentário via moderação."""
        comment = Comment.objects.create(
            article=self.article,
            name='Delete User',
            email='delete@example.com',
            content='Delete comment'
        )

        self.client.login(email='staff@example.com', password='testpass123')

        url = reverse('articles:moderate_comment_action', kwargs={'comment_id': comment.id})
        response = self.client.post(url, {'action': 'delete'})

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Comment.objects.filter(id=comment.id).exists())

    @patch('apps.articles.views.comment_views.ratelimit')
    def test_rate_limiting(self, mock_ratelimit):
        """Testa rate limiting nos comentários."""
        mock_ratelimit.return_value = lambda func: func

        url = reverse('articles:add_comment', kwargs={'slug': self.article.slug})
        data = {
            'name': 'Rate Test',
            'email': 'rate@example.com',
            'content': 'Rate limiting test comment.',
            'website_url': ''
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)

        # Verificar se o decorator foi aplicado
        mock_ratelimit.assert_called()

    def test_comment_stats_staff_only(self):
        """Testa que estatísticas são apenas para staff."""
        url = reverse('articles:comment_stats')

        # Usuário não autenticado
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        # Usuário comum
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        # Staff
        self.client.login(email='staff@example.com', password='testpass123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        json_response = response.json()
        self.assertIn('total_comments', json_response)
        self.assertIn('approved_comments', json_response)
        self.assertIn('pending_comments', json_response)
        self.assertIn('spam_comments', json_response)
