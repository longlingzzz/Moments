from django.urls import path
from .views import (
    get_notifications,
    mark_notification_read,
    mark_all_notifications_read,
    delete_notification,
    delete_all_notifications
)

app_name = 'notifications'

urlpatterns = [
    # 获取通知列表
    path('api/notifications/', get_notifications, name='get_notifications'),
    # 标记单个通知为已读
    path('api/notifications/<int:notification_id>/read/', mark_notification_read, name='mark_notification_read'),
    # 标记所有通知为已读
    path('api/notifications/read-all/', mark_all_notifications_read, name='mark_all_notifications_read'),
    # 删除单个通知
    path('api/notifications/<int:notification_id>/delete/', delete_notification, name='delete_notification'),
    # 删除所有通知
    path('api/notifications/delete-all/', delete_all_notifications, name='delete_all_notifications'),
]
