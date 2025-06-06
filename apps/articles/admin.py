from django.contrib import admin
from apps.articles.models import Article, Category, Tag, Comment

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin para categorias"""
    list_display = ['name', 'slug', 'parent', 'is_active', 'order', 'article_count']
    list_filter = ['is_active', 'parent']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']

    def article_count(self, obj):
        return obj.get_article_count()
    article_count.short_description = 'Artigos'

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Admin para tags"""
    list_display = ['name', 'slug', 'is_featured', 'article_count', 'created_at']
    list_filter = ['is_featured', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}

    def article_count(self, obj):
        return obj.get_article_count()
    article_count.short_description = 'Artigos'

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """Admin para artigos"""
    list_display = ['title', 'author', 'category', 'status', 'is_featured', 'view_count', 'published_at']
    list_filter = ['status', 'is_featured', 'category', 'created_at', 'published_at']
    search_fields = ['title', 'excerpt', 'content']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['view_count', 'reading_time', 'created_at', 'updated_at']
    filter_horizontal = ['tags', 'contributors']

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('title', 'slug', 'excerpt', 'content', 'featured_image', 'featured_image_alt')
        }),
        ('Classificação', {
            'fields': ('category', 'tags')
        }),
        ('Autoria', {
            'fields': ('author', 'contributors')
        }),
        ('Publicação', {
            'fields': ('status', 'is_featured', 'allow_comments', 'published_at', 'scheduled_at')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Estatísticas', {
            'fields': ('view_count', 'reading_time', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # Criando novo
            obj.author = request.user
        super().save_model(request, obj, form, change)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin para comentários"""
    list_display = ['name', 'article', 'is_approved', 'is_spam', 'created_at']
    list_filter = ['is_approved', 'is_spam', 'created_at']
    search_fields = ['name', 'email', 'content']
    readonly_fields = ['ip_address', 'user_agent', 'created_at', 'updated_at']

    actions = ['approve_comments', 'mark_as_spam']

    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True, is_spam=False)
    approve_comments.short_description = "Aprovar comentários selecionados"

    def mark_as_spam(self, request, queryset):
        queryset.update(is_spam=True, is_approved=False)
    mark_as_spam.short_description = "Marcar como spam"
