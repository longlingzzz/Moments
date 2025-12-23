from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.utils import timezone
from rest_framework.decorators import permission_classes

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """健康检查接口"""
    return Response({
        'status': 'healthy',
        'timestamp': timezone.now(),
        'message': 'Django API Backend is running'
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def api_info(request):
    """API 信息接口"""
    return Response({
        'name': 'Django API Backend',
        'version': '1.0.0',
        'description': '纯后端 API 服务',
        'authentication': 'Bearer Token or Session Authentication required for protected endpoints',
        'public_endpoints': [
            'GET /api/health/',
            'GET /api/info/',
            'POST /api/users/register/',
            'POST /api/auth/login/'
        ],
        'protected_endpoints': [
            'GET /api/users/',
            'GET /api/users/me/',
            'PUT /api/users/{id}/',
            'DELETE /api/users/{id}/',
            'POST /api/auth/logout/'
        ],
        'endpoints': {
            'health': '/api/health/',
            'info': '/api/info/',
            'users': '/api/users/',
            'user_register': '/api/users/register/',
            'current_user': '/api/users/me/',
            'login': '/api/auth/login/',
            'logout': '/api/auth/logout/'
        }
    })