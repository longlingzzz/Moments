from rest_framework import viewsets, status, pagination
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from api.models import Post, Like, Comment
from my.serializers import PostSerializer, CommentSerializer, CreateCommentSerializer


# 自定义分页类
class StandardResultsSetPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'pageSize'
    max_page_size = 100


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_posts(request):
    """获取我的动态列表接口"""
    page = request.query_params.get('page', 1)
    page_size = request.query_params.get('pageSize', 10)
    
    # 按时间倒序获取当前用户的动态
    posts = Post.objects.filter(user=request.user).order_by('-created_at')
    
    # 分页
    paginator = StandardResultsSetPagination()
    paginator.page_size = page_size
    result_page = paginator.paginate_queryset(posts, request)
    
    # 序列化
    serializer = PostSerializer(result_page, many=True, context={'request': request})
    
    return paginator.get_paginated_response({
        'success': True,
        'data': {
            'posts': serializer.data,
            'total': posts.count()
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_stats(request):
    """获取我的统计信息接口"""
    # 统计当前用户的动态数量
    posts_count = Post.objects.filter(user=request.user).count()
    
    return Response({
        'success': True,
        'data': {
            'posts': posts_count
        }
    })


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_my_post(request, post_id):
    """删除我的动态接口"""
    try:
        # 确保只能删除自己的动态
        post = Post.objects.get(id=post_id, user=request.user)
        post.delete()
        
        return Response({
            'success': True,
            'message': '删除成功'
        })
    except Post.DoesNotExist:
        return Response({
            'success': False,
            'message': '动态不存在或无权删除'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_like(request, post_id):
    """点赞/取消点赞接口"""
    try:
        post = Post.objects.get(id=post_id)
        liked = request.data.get('liked', True)
        
        if liked:
            # 点赞
            like, created = Like.objects.get_or_create(user=request.user, post=post)
            if not created:
                # 已经点赞过
                return Response({
                    'success': False,
                    'message': '已经点赞过'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            # 取消点赞
            try:
                like = Like.objects.get(user=request.user, post=post)
                like.delete()
            except Like.DoesNotExist:
                return Response({
                    'success': False,
                    'message': '未点赞过该动态'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # 更新点赞数
        post.refresh_from_db()
        
        return Response({
            'success': True,
            'message': '操作成功',
            'data': {
                'likes': post.likes_count
            }
        })
    except Post.DoesNotExist:
        return Response({
            'success': False,
            'message': '动态不存在'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def post_comments(request, post_id):
    """获取动态评论列表和发布评论接口"""
    try:
        post = Post.objects.get(id=post_id)
        
        if request.method == 'GET':
            # 获取评论列表
            page = request.query_params.get('page', 1)
            page_size = request.query_params.get('pageSize', 10)
            
            # 按时间倒序获取评论
            comments = Comment.objects.filter(post=post).order_by('-created_at')
            
            # 分页
            paginator = StandardResultsSetPagination()
            paginator.page_size = page_size
            result_page = paginator.paginate_queryset(comments, request)
            
            # 序列化
            serializer = CommentSerializer(result_page, many=True, context={'request': request})
            
            return paginator.get_paginated_response({
                'success': True,
                'data': {
                    'comments': serializer.data,
                    'total': comments.count()
                }
            })
        elif request.method == 'POST':
            # 发布评论
            serializer = CreateCommentSerializer(data=request.data)
            
            if serializer.is_valid():
                comment = serializer.save(user=request.user, post=post)
                
                # 序列化返回的评论
                comment_serializer = CommentSerializer(comment, context={'request': request})
                
                return Response({
                    'success': True,
                    'message': '评论成功',
                    'data': comment_serializer.data
                }, status=status.HTTP_201_CREATED)
            
            return Response({
                'success': False,
                'message': '评论失败',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    except Post.DoesNotExist:
        return Response({
            'success': False,
            'message': '动态不存在'
        }, status=status.HTTP_404_NOT_FOUND)
