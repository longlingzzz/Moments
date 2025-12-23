from django.db import models

# Create your models here.

####################  搜索部分开始  ######################
from django.contrib.auth import get_user_model
User = get_user_model()

# --------------- 1.Post  ---------------
class Post(models.Model):
    """动态/朋友圈"""
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    text = models.TextField()
    type = models.CharField(max_length=10, choices=[('image','image'),('video','video')])
    media = models.JSONField(default=list, blank=True)   # ["url1","url2"]
    tag  = models.CharField(max_length=20, blank=True)
    likes = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

# --------------- 2.搜索历史  ---------------
class SearchHistory(models.Model):
    """用户搜索历史"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    keyword = models.CharField(max_length=50)
    tag = models.CharField(max_length=20, blank=True)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

# --------------- 3.点赞  ---------------
class Like(models.Model):
    """点赞"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='like_set')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')   # 一人只能点赞一次

# --------------- 4.评论 ---------------
class Comment(models.Model):
    """评论"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comment_set')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
####################  搜索部分结束  ######################