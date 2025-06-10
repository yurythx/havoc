from django import forms
from django.core.exceptions import ValidationError
from apps.articles.models.article import Article
from apps.articles.models.category import Category
from apps.articles.models.tag import Tag


class ArticleForm(forms.ModelForm):
    """Formulário para criação e edição de artigos"""
    
    class Meta:
        model = Article
        fields = [
            'title', 'excerpt', 'content', 'featured_image', 'featured_image_alt',
            'category', 'tags', 'status', 'is_featured', 'allow_comments',
            'meta_title', 'meta_description', 'meta_keywords'
        ]
        
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Digite o título do artigo...',
                'maxlength': 200
            }),
            'excerpt': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Escreva um resumo atrativo do artigo...',
                'rows': 3,
                'maxlength': 500
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Escreva o conteúdo completo do artigo...',
                'rows': 15
            }),
            'featured_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'featured_image_alt': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Texto alternativo para a imagem...',
                'maxlength': 200
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'tags': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': '5'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'allow_comments': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'meta_title': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'Título para SEO (máx. 60 caracteres)',
                'maxlength': 60
            }),
            'meta_description': forms.Textarea(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'Descrição para SEO (máx. 160 caracteres)',
                'rows': 3,
                'maxlength': 160
            }),
            'meta_keywords': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'Palavras-chave separadas por vírgula',
                'maxlength': 200
            }),
        }
        
        labels = {
            'title': 'Título',
            'excerpt': 'Resumo',
            'content': 'Conteúdo',
            'featured_image': 'Imagem Destacada',
            'featured_image_alt': 'Texto Alternativo',
            'category': 'Categoria',
            'tags': 'Tags',
            'status': 'Status',
            'is_featured': 'Artigo em destaque',
            'allow_comments': 'Permitir comentários',
            'meta_title': 'Meta Título',
            'meta_description': 'Meta Descrição',
            'meta_keywords': 'Palavras-chave',
        }
        
        help_texts = {
            'title': 'Título principal do artigo (máximo 200 caracteres)',
            'excerpt': 'Resumo que aparecerá na listagem de artigos (máximo 500 caracteres)',
            'content': 'Conteúdo completo do artigo (pode usar HTML)',
            'featured_image': 'Imagem que aparecerá no topo do artigo e na listagem',
            'featured_image_alt': 'Texto alternativo para acessibilidade',
            'category': 'Categoria principal do artigo',
            'tags': 'Segure Ctrl/Cmd para selecionar múltiplas tags',
            'status': 'Status de publicação do artigo',
            'is_featured': 'Marque para destacar o artigo na página inicial',
            'allow_comments': 'Permitir que usuários comentem no artigo',
            'meta_title': 'Título para mecanismos de busca (máximo 60 caracteres)',
            'meta_description': 'Descrição para mecanismos de busca (máximo 160 caracteres)',
            'meta_keywords': 'Palavras-chave para SEO, separadas por vírgula',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configurar queryset para categoria
        self.fields['category'].queryset = Category.objects.all()
        self.fields['category'].empty_label = "Selecione uma categoria"
        
        # Configurar queryset para tags
        self.fields['tags'].queryset = Tag.objects.all()
        
        # Tornar campos obrigatórios
        self.fields['title'].required = True
        self.fields['excerpt'].required = True
        self.fields['content'].required = True
        
        # Configurar valores padrão
        if not self.instance.pk:  # Novo artigo
            self.fields['status'].initial = 'draft'
            self.fields['allow_comments'].initial = True

    def clean_title(self):
        """Validação personalizada para o título"""
        title = self.cleaned_data.get('title')
        if title:
            # Verificar se já existe um artigo com o mesmo título (exceto o atual)
            existing = Article.objects.filter(title__iexact=title)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise ValidationError('Já existe um artigo com este título.')
        
        return title

    def clean_excerpt(self):
        """Validação personalizada para o resumo"""
        excerpt = self.cleaned_data.get('excerpt')
        if excerpt and len(excerpt) < 50:
            raise ValidationError('O resumo deve ter pelo menos 50 caracteres.')
        return excerpt

    def clean_content(self):
        """Validação personalizada para o conteúdo"""
        content = self.cleaned_data.get('content')
        if content and len(content) < 100:
            raise ValidationError('O conteúdo deve ter pelo menos 100 caracteres.')
        return content

    def clean_meta_title(self):
        """Validação para meta título"""
        meta_title = self.cleaned_data.get('meta_title')
        if meta_title and len(meta_title) > 60:
            raise ValidationError('O meta título não pode ter mais de 60 caracteres.')
        return meta_title

    def clean_meta_description(self):
        """Validação para meta descrição"""
        meta_description = self.cleaned_data.get('meta_description')
        if meta_description and len(meta_description) > 160:
            raise ValidationError('A meta descrição não pode ter mais de 160 caracteres.')
        return meta_description

    def clean_featured_image(self):
        """Validação para imagem destacada"""
        image = self.cleaned_data.get('featured_image')
        if image:
            # Verificar tamanho do arquivo (máximo 5MB)
            if image.size > 5 * 1024 * 1024:
                raise ValidationError('A imagem não pode ser maior que 5MB.')
            
            # Verificar tipo de arquivo
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
            if hasattr(image, 'content_type') and image.content_type not in allowed_types:
                raise ValidationError('Tipo de arquivo não permitido. Use JPEG, PNG, GIF ou WebP.')
        
        return image

    def save(self, commit=True):
        """Sobrescrever save para adicionar lógica personalizada"""
        article = super().save(commit=False)
        
        # Se não há meta_title, usar o título
        if not article.meta_title:
            article.meta_title = article.title[:60]
        
        # Se não há meta_description, usar o excerpt
        if not article.meta_description:
            article.meta_description = article.excerpt[:160]
        
        if commit:
            article.save()
            self.save_m2m()  # Salvar tags
        
        return article
