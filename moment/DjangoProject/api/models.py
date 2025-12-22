from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    """扩展用户资料"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    # 用 CharField 兼容 H5/小程序本地路径、网络 URL
    avatar = models.CharField(max_length=500, blank=True, default='')
    signature = models.CharField(max_length=120, blank=True, default='')

    def __str__(self):
        return f'Profile({self.user.username})'


class Post(models.Model):
    """动态模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    text = models.TextField(blank=True, default='')
    type = models.CharField(max_length=20, default='text')  # image, text, etc.
    media = models.JSONField(default=list)  # 存储媒体URL列表
    created_at = models.DateTimeField(auto_now_add=True)
    likes_count = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)

    def __str__(self):
        return f'Post({self.id}) by {self.user.username}'


class Like(models.Model):
    """点赞模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')  # 一个用户只能给一个动态点赞一次

    def __str__(self):
        return f'Like by {self.user.username} on Post({self.post.id})'


class Comment(models.Model):
    """评论模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.user.username} on Post({self.post.id})'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()


@receiver(post_save, sender=Like)
def update_likes_count(sender, instance, created, **kwargs):
    """点赞后更新动态的点赞数"""
    if created:
        instance.post.likes_count += 1
        instance.post.save()


@receiver(post_save, sender=Comment)
def update_comments_count(sender, instance, created, **kwargs):
    """评论后更新动态的评论数"""
    if created:
        instance.post.comments_count += 1
        instance.post.save()


@receiver(models.signals.post_delete, sender=Like)
def update_likes_count_delete(sender, instance, **kwargs):
    """取消点赞后更新动态的点赞数"""
    instance.post.likes_count = max(0, instance.post.likes_count - 1)
    instance.post.save()


@receiver(models.signals.post_delete, sender=Comment)
def update_comments_count_delete(sender, instance, **kwargs):
    """删除评论后更新动态的评论数"""
    instance.post.comments_count = max(0, instance.post.comments_count - 1)
    instance.post.save()
