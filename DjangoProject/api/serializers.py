from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Post, SearchHistory    # 搜索部分的引用

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name']
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

####################  搜索部分新增  ######################
# --------------- 1.Post  ---------------
class PostSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='author.username', read_only=True)
    avatar = serializers.SerializerMethodField()
    time = serializers.SerializerMethodField()
    liked = serializers.SerializerMethodField()
    # 尝试实时更新评论数
    comments = serializers.IntegerField(source='comment_set.count', read_only=True)

    class Meta:
        model = Post
        fields = ['id','name','avatar','time','text','type','media',
                  'tag','likes','comments','liked']

    def get_avatar(self, obj):
        # 用户头像字段，如无则返回默认
        return getattr(obj.author, 'avatar', 'https://picsum.photos/200')

    def get_time(self, obj):
        # 友好时间
        from django.utils.timesince import timesince
        return timesince(obj.created_at, locale='zh_CN') + '前'

    def get_liked(self, obj):
        # 当前登录用户是否点过赞（需传request上下文）
        user = self.context['request'].user
        if user.is_authenticated:
            return obj.like_set.filter(user=user).exists()
        return False

# --------------- 2.搜索历史  ---------------
class SearchHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchHistory
        fields = ['keyword','tag','date']

# --------------- 3.评论 ---------------
class CommentSerializer(serializers.ModelSerializer):
    name   = serializers.CharField(source='user.username', read_only=True)
    avatar = serializers.SerializerMethodField()
    time   = serializers.SerializerMethodField()

    class Meta:
        model  = Comment
        fields = ['id','name','avatar','content','time']

    def get_avatar(self, obj):
        return getattr(obj.user, 'avatar', 'https://picsum.photos/200')

    def get_time(self, obj):
        from django.utils.timesince import timesince
        return timesince(obj.created_at, locale='zh_CN') + '前'

# --------------- 4.点赞  ---------------
# 点赞/取消点赞后返回的最新数据
class PostLikeRespSerializer(serializers.ModelSerializer):
    likes = serializers.IntegerField(read_only=True)
    liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['likes','liked']

    def get_liked(self, obj):
        user = self.context['request'].user
        return obj.like_set.filter(user=user).exists() if user.is_authenticated else False
####################  搜索部分结束  ######################