from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .serializers import UserSerializer, UserCreateSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]  # 默认允许匿名访问
    
    def get_permissions(self):
        """根据动作设置不同的权限"""
        if self.action in ['list', 'retrieve', 'create', 'update', 'partial_update', 'destroy', 'me']:
            return [IsAuthenticated()]  # 列表、详情、创建、更新、删除和获取当前用户信息需要认证
        return [AllowAny()]  # register 允许匿名访问
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    def create(self, request, *args, **kwargs):
        """重写创建方法，使用注册逻辑"""
        return self.register(request)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """获取当前用户信息"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post', 'get'], permission_classes=[AllowAny])
    def register(self, request):
        """用户注册"""
        if request.method == 'GET':
            return Response({
                'message': 'This is the user registration endpoint.',
                'method': 'POST',
                'required_fields': ['username', 'password'],
                'optional_fields': ['email', 'first_name', 'last_name'],
                'example': {
                    'username': 'newuser',
                    'password': 'securepassword',
                    'email': 'user@example.com'
                }
            })
        
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message': 'User created successfully',
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """用户登录接口"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({
            'error': 'Please provide both username and password'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(username=username, password=password)
    
    if user is not None:
        # 获取或创建 token
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'message': 'Login successful',
            'token': token.key,
            'user': UserSerializer(user).data
        })
    else:
        return Response({
            'error': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """用户登出接口"""
    try:
        # 删除用户的 token
        Token.objects.filter(user=request.user).delete()
        return Response({
            'message': 'Logout successful'
        })
    except Token.DoesNotExist:
        return Response({
            'message': 'No active session found'
        }, status=status.HTTP_400_BAD_REQUEST)

####################  搜索部分开始  ######################
# 7号接口之前也有import
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count
from .models import Post, SearchHistory
from .serializers import PostSerializer, SearchHistorySerializer
from datetime import datetime

# --------------- 1.搜索接口  ---------------
class SearchView(generics.GenericAPIView):
    """
    GET /api/search ?keyword=&tag=&date=&page=&pageSize=
    支持关键词、标签和日期的组合筛选
    """
    serializer_class = PostSerializer

    def get(self, request):
        kw   = request.GET.get('keyword','').strip()
        tag  = request.GET.get('tag','').strip()
        date = request.GET.get('date','')          # YYYY-MM-DD
        page = int(request.GET.get('page',1))
        pz   = int(request.GET.get('pageSize',10))

        qs = Post.objects.all()
        if kw:
            qs = qs.filter(Q(text__icontains=kw)|Q(author__username__icontains=kw))
        if tag:
            qs = qs.filter(tag=tag)
        if date:
            try:
                d = datetime.strptime(date,'%Y-%m-%d').date()
                qs = qs.filter(created_at__date=d)
            except ValueError:
                pass

        total = qs.count()
        start = (page-1)*pz
        posts = qs[start:start+pz]

        ser = PostSerializer(posts, many=True, context={'request':request})
        return Response({'success':True,
                         'data':{'results':ser.data,'total':total}})

# --------------- 2.热门标签接口  ---------------
class HotTagsView(generics.GenericAPIView):
    """
    GET /api/tags/hot
    """
    def get(self, request):
        # 按 tag 出现次数倒序
        tags = (Post.objects.values('tag')
                            .annotate(c=Count('id'))
                            .order_by('-c')[:20])
        data = [t['tag'] for t in tags if t['tag']]
        return Response({'success':True,'data':{'tags':data}})

# --------------- 3.搜索建议接口  ---------------
class SearchSuggestionsView(generics.GenericAPIView):
    """
    GET /api/search/suggestions ?keyword=
    """
    def get(self, request):
        kw = request.GET.get('keyword','').strip()
        if not kw:
            return Response({'success':True,'data':{'suggestions':[]}})
        # 简单示范：从用户名、tag、历史关键词中模糊匹配
        user_qs = User.objects.filter(username__icontains=kw)[:5]
        tag_qs  = (Post.objects.filter(tag__icontains=kw)
                               .values_list('tag',flat=True).distinct()[:5])
        hist_qs = (SearchHistory.objects.filter(keyword__icontains=kw)
                                        .values_list('keyword',flat=True)
                                        .distinct()[:5])
        sugs = list({u.username for u in user_qs}) + list(tag_qs) + list(hist_qs)
        sugs = list(dict.fromkeys(sugs))[:10]   # 去重
        return Response({'success':True,'data':{'suggestions':sugs}})

# --------------- 4.保存搜索历史  ---------------
class SearchHistorySaveView(generics.GenericAPIView):
    """
    POST /api/search/history
    """
    permission_classes = [IsAuthenticated]
    def post(self, request):
        keyword = request.data.get('keyword','').strip()
        tag     = request.data.get('tag','').strip()
        date    = request.data.get('date','')
        if not keyword:
            return Response({'success':False,'message':'关键词不能为空'},status=400)
        SearchHistory.objects.update_or_create(
            user=request.user,
            keyword=keyword,
            tag=tag,
            date=date or datetime.today().date(),
            defaults={'created_at':datetime.now()}
        )
        return Response({'success':True,'message':'搜索历史已保存'})

# --------------- 5.获取搜索历史  ---------------
class SearchHistoryListView(generics.GenericAPIView):
    """
    GET /api/search/history ?page=&pageSize=
    支持分页，默认 10 条/页
    """
    permission_classes = [IsAuthenticated]
    serializer_class = SearchHistorySerializer
    pagination_class = StandardResultSetPagination

    def get_queryset(self):
        return SearchHistory.objects.filter(user=self.request.user)

# --------------- 6.清楚搜索历史  ---------------
class SearchHistoryClearView(generics.GenericAPIView):
    """
    DELETE /api/search/history/clear
    """
    permission_classes = [IsAuthenticated]
    def delete(self, request):
        SearchHistory.objects.filter(user=request.user).delete()
        return Response({'success':True,'message':'搜索历史已清除'})

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Post, Like, Comment


# --------------- 7. 点赞/取消点赞  ---------------
class StandardResultSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'pageSize'
    page_query_param = 'page'


class PostLikeView(generics.GenericAPIView):
    """
    POST /api/posts/<id>/like
    Body: {"liked": true/false}
    返回最新的 likes & liked 状态
    """
    serializer_class = PostLikeRespSerializer
    pagination_class = None

    @transaction.atomic
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        liked = request.data.get('liked')
        if liked is None:
            return Response({'success': False, 'message': 'liked 字段必填'}, status=400)

        if liked:
            # 点赞（忽略重复）
            Like.objects.get_or_create(user=request.user, post=post)
        else:
            # 取消点赞
            Like.objects.filter(user=request.user, post=post).delete()

        # 重新统计
        post.likes = post.like_set.count()
        post.save(update_fields=['likes'])
        ser = self.get_serializer(post)
        return Response({'success': True,
                         'message': '操作成功',
                         'data': ser.data})


# --------------- 8. 获取评论列表  ---------------
class PostCommentListView(generics.ListAPIView):
    """
    GET /api/posts/<id>/comments ?page=&pageSize=
    """
    serializer_class = CommentSerializer
    pagination_class = StandardResultSetPagination

    def get_queryset(self):
        post = get_object_or_404(Post, pk=self.kwargs['pk'])
        return post.comment_set.select_related('user')


# --------------- 9. 发布评论  ---------------
class PostCommentCreateView(generics.GenericAPIView):
    """
    POST /api/posts/<id>/comments
    Body: {"content": "xxx"}
    返回最新插入的单条评论
    """
    serializer_class = CommentSerializer

    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        content = request.data.get('content', '').strip()
        if not content:
            return Response({'success': False, 'message': '评论内容不能为空'}, status=400)
        c = Comment.objects.create(post=post, user=request.user, content=content)
        # 同步更新评论数（可选）
        post.comments = post.comment_set.count()
        post.save(update_fields=['comments'])
        ser = self.get_serializer(c, context={'request': request})
        return Response({'success': True,
                         'message': '评论成功',
                         'data': ser.data})

####################  搜索部分结束  ######################
