from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver


class Notification(models.Model):
    """通知模型"""
    # 通知类型
    NOTIFICATION_TYPES = (
        ('like', '点赞'),
        ('comment', '评论'),
        ('follow', '关注'),
        ('system', '系统通知'),
    )
    
    # 接收通知的用户
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    # 通知类型
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    # 执行操作的用户
    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    # 关联的对象（如动态、评论等）
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    # 通知内容
    message = models.CharField(max_length=255)
    # 是否已读
    is_read = models.BooleanField(default=False)
    # 创建时间
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f'Notification to {self.user.username} from {self.actor.username}: {self.message}'


@receiver(post_save, sender='api.Like')
def create_like_notification(sender, instance, created, **kwargs):
    """创建点赞通知"""
    if created:
        # 不通知自己
        if instance.user != instance.post.user:
            Notification.objects.create(
                user=instance.post.user,
                type='like',
                actor=instance.user,
                content_object=instance.post,
                message=f'{instance.user.username} 点赞了你的动态'
            )


@receiver(post_save, sender='api.Comment')
def create_comment_notification(sender, instance, created, **kwargs):
    """创建评论通知"""
    if created:
        # 不通知自己
        if instance.user != instance.post.user:
            Notification.objects.create(
                user=instance.post.user,
                type='comment',
                actor=instance.user,
                content_object=instance.comment,
                message=f'{instance.user.username} 评论了你的动态'
            )
