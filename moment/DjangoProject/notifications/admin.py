from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """通知管理后台配置"""
    list_display = ('id', 'user', 'type', 'actor', 'message', 'is_read', 'created_at')
    list_filter = ('type', 'is_read', 'created_at')
    search_fields = ('user__username', 'actor__username', 'message')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
