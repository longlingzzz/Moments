# 从api应用中导入序列化器，保持代码一致性
from api.serializers import (
    PostSerializer,
    CommentSerializer,
    CreateCommentSerializer,
    LikeSerializer,
    UserSerializer,
    ProfileSerializer
)

# 也可以在这里添加my应用特有的序列化器