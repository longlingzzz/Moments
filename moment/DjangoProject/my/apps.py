from django.apps import AppConfig


class MyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'my'
    verbose_name = '我的页面'
