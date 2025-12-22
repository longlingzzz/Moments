from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Notification
from .serializers import NotificationSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_notifications(request):
    """获取当前用户的通知列表"""
    # 获取通知列表，按时间倒序
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    # 序列化
    serializer = NotificationSerializer(notifications, many=True, context={'request': request})
    
    return Response({
        'success': True,
        'data': {
            'notifications': serializer.data,
            'total': notifications.count(),
            'unread': notifications.filter(is_read=False).count()
        }
    })


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def mark_notification_read(request, notification_id):
    """标记单个通知为已读"""
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.is_read = True
        notification.save()
        
        return Response({
            'success': True,
            'message': '通知已标记为已读'
        })
    except Notification.DoesNotExist:
        return Response({
            'success': False,
            'message': '通知不存在或无权操作'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def mark_all_notifications_read(request):
    """标记所有通知为已读"""
    # 更新当前用户的所有未读通知
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    
    return Response({
        'success': True,
        'message': '所有通知已标记为已读'
    })


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_notification(request, notification_id):
    """删除单个通知"""
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.delete()
        
        return Response({
            'success': True,
            'message': '通知已删除'
        })
    except Notification.DoesNotExist:
        return Response({
            'success': False,
            'message': '通知不存在或无权操作'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_all_notifications(request):
    """删除所有通知"""
    # 删除当前用户的所有通知
    Notification.objects.filter(user=request.user).delete()
    
    return Response({
        'success': True,
        'message': '所有通知已删除'
    })
