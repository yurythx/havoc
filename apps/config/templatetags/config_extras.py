from django import template
import json
import pprint as pp

register = template.Library()


@register.filter
def pprint(value):
    """Pretty print para JSON e dicionários"""
    try:
        if isinstance(value, str):
            # Tentar fazer parse do JSON
            parsed = json.loads(value)
            return json.dumps(parsed, indent=2, ensure_ascii=False)
        elif isinstance(value, dict):
            return json.dumps(value, indent=2, ensure_ascii=False)
        else:
            return pp.pformat(value, indent=2)
    except:
        return str(value)


@register.filter
def get_item(dictionary, key):
    """Obter item de dicionário no template"""
    return dictionary.get(key)


@register.simple_tag
def config_status_badge(is_active, is_default=False):
    """Gera badge de status para configurações"""
    badges = []
    
    if is_active:
        badges.append('<span class="badge bg-success">Ativo</span>')
    else:
        badges.append('<span class="badge bg-secondary">Inativo</span>')
    
    if is_default:
        badges.append('<span class="badge bg-warning text-dark"><i class="fas fa-star me-1"></i>Padrão</span>')
    
    return ' '.join(badges)


@register.inclusion_tag('config/includes/test_result_badge.html')
def test_result_badge(last_test_result):
    """Renderiza badge do resultado do teste"""
    return {
        'result': last_test_result,
        'success': last_test_result.get('success', False) if last_test_result else False,
        'message': last_test_result.get('message', '') if last_test_result else ''
    }


@register.filter
def engine_icon(engine):
    """Retorna ícone baseado no engine do banco"""
    icons = {
        'django.db.backends.postgresql': 'fas fa-database text-info',
        'django.db.backends.mysql': 'fas fa-database text-warning',
        'django.db.backends.sqlite3': 'fas fa-file-alt text-secondary',
        'django.db.backends.oracle': 'fas fa-database text-danger',
    }
    return icons.get(engine, 'fas fa-database text-muted')


@register.filter
def connection_string(config):
    """Gera string de conexão para exibição (sem senha)"""
    if hasattr(config, 'engine'):
        # Database config
        if config.engine == 'django.db.backends.sqlite3':
            return f"sqlite:///{config.name_db}"
        elif config.host:
            return f"{config.get_engine_display().lower()}://{config.user}@{config.host}:{config.port}/{config.name_db}"
        else:
            return f"{config.get_engine_display().lower()}://localhost/{config.name_db}"
    else:
        # Email config
        protocol = "smtps" if config.email_use_ssl else "smtp"
        if config.email_use_tls:
            protocol += "+tls"
        return f"{protocol}://{config.email_host}:{config.email_port}"


@register.simple_tag
def config_count_badge(count, label, color="primary"):
    """Gera badge com contador"""
    return f'<span class="badge bg-{color}">{count}</span> {label}'
