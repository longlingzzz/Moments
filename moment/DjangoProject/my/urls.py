from django.urls import path, include
from .views import (
    get_my_posts,
    get_my_stats,
    delete_my_post,
    toggle_like,
    post_comments,
)


urlpatterns = [
    # 我的动态相关接口
    path('posts/', get_my_posts, name='my-posts'),
    path('posts/<int:post_id>/', delete_my_post, name='delete-my-post'),
    path('posts/<int:post_id>/like/', toggle_like, name='toggle-like'),
    path('posts/<int:post_id>/comments/', post_comments, name='post-comments'),
    
    # 我的统计信息
    path('stats/', get_my_stats, name='my-stats'),
]
