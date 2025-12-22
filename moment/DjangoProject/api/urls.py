from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, 
    login_view, 
    logout_view,
    get_my_posts,
    get_my_stats,
    delete_my_post,
    toggle_like,
    post_comments,
)
from .utils import health_check, api_info

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('health/', health_check, name='health-check'),
    path('info/', api_info, name='api-info'),
    path('auth/login/', login_view, name='login'),
    path('auth/logout/', logout_view, name='logout'),
    path('', include(router.urls)),
    
    # 用户动态相关接口
    path('user/posts/', get_my_posts, name='my-posts'),
    path('user/posts/<int:post_id>/', delete_my_post, name='delete-my-post'),
    path('user/stats/', get_my_stats, name='my-stats'),
    
    # 动态交互接口
    path('posts/<int:post_id>/like/', toggle_like, name='toggle-like'),
    path('posts/<int:post_id>/comments/', post_comments, name='post-comments'),
]