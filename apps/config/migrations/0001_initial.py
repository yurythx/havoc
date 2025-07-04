# Generated by Django 5.2.2 on 2025-06-06 14:13

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SystemConfiguration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(help_text='Chave única da configuração', max_length=100, unique=True, validators=[django.core.validators.MinLengthValidator(3)], verbose_name='chave')),
                ('value', models.TextField(help_text='Valor da configuração (pode ser JSON)', verbose_name='valor')),
                ('description', models.TextField(blank=True, help_text='Descrição da configuração', verbose_name='descrição')),
                ('is_active', models.BooleanField(default=True, help_text='Se a configuração está ativa', verbose_name='ativo')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='atualizado em')),
                ('updated_by', models.ForeignKey(blank=True, help_text='Usuário que fez a última atualização', null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='atualizado por')),
            ],
            options={
                'verbose_name': 'configuração do sistema',
                'verbose_name_plural': 'configurações do sistema',
                'ordering': ['key'],
            },
        ),
        migrations.CreateModel(
            name='UserActivityLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('CREATE', 'Criação'), ('UPDATE', 'Atualização'), ('DELETE', 'Exclusão'), ('LOGIN', 'Login'), ('LOGOUT', 'Logout'), ('PASSWORD_CHANGE', 'Alteração de Senha'), ('PERMISSION_CHANGE', 'Alteração de Permissão'), ('GROUP_CHANGE', 'Alteração de Grupo')], max_length=20, verbose_name='ação')),
                ('description', models.TextField(help_text='Descrição detalhada da ação', verbose_name='descrição')),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True, verbose_name='endereço IP')),
                ('user_agent', models.TextField(blank=True, help_text='Informações do navegador/cliente', verbose_name='user agent')),
                ('extra_data', models.JSONField(blank=True, default=dict, help_text='Dados adicionais em formato JSON', verbose_name='dados extras')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='criado em')),
                ('target_user', models.ForeignKey(blank=True, help_text='Usuário que foi afetado pela ação (se aplicável)', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='target_logs', to=settings.AUTH_USER_MODEL, verbose_name='usuário alvo')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activity_logs', to=settings.AUTH_USER_MODEL, verbose_name='usuário')),
            ],
            options={
                'verbose_name': 'log de atividade',
                'verbose_name_plural': 'logs de atividade',
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['user', '-created_at'], name='config_user_user_id_deeb8b_idx'), models.Index(fields=['action', '-created_at'], name='config_user_action_a6f429_idx'), models.Index(fields=['target_user', '-created_at'], name='config_user_target__739c91_idx')],
            },
        ),
    ]
