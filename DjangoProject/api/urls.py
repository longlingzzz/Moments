from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, login_view, logout_view
from .utils import health_check, api_info
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('health/', health_check, name='health-check'),
    path('info/', api_info, name='api-info'),
    path('auth/login/', login_view, name='login'),
    path('auth/logout/', logout_view, name='logout'),
    path('', include(router.urls)),
]


###  搜索部分新增url（共⑨个）  ###
from .views import (
    SearchView, HotTagsView, SearchSuggestionsView,
    SearchHistorySaveView, SearchHistoryListView, SearchHistoryClearView
)
urlpatterns += [
    path('search', SearchView.as_view(), name='search'),
    path('tags/hot', HotTagsView.as_view(), name='hot-tags'),
    path('search/suggestions', SearchSuggestionsView.as_view(), name='suggestions'),
    path('search/history', SearchHistorySaveView.as_view(), name='save-history'),
    path('search/history/list', SearchHistoryListView.as_view(), name='list-history'),
    path('search/history/clear', SearchHistoryClearView.as_view(), name='clear-history'),
    path('posts/<int:pk>/like', PostLikeView.as_view(), name='post-like'),
    path('posts/<int:pk>/comments', PostCommentListView.as_view(), name='post-comment-list'),
    path('posts/<int:pk>/comments/add', PostCommentCreateView.as_view(), name='post-comment-add'),
]
####################