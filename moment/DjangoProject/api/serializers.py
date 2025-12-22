from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from .models import Profile, Post, Like, Comment


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['avatar', 'signature']


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True, required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined', 'profile']
        read_only_fields = ['id', 'date_joined']

    def to_representation(self, instance):
        # 确保旧用户也有 profile 以避免序列化时报错
        Profile.objects.get_or_create(user=instance)
        return super().to_representation(instance)


class UserUpdateSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'profile']

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        user = super().update(instance, validated_data)
        if profile_data:
            profile, _ = Profile.objects.get_or_create(user=user)
            serializer = ProfileSerializer(profile, data=profile_data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return user


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name']
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("旧密码不正确")
        return value

    def validate_new_password(self, value):
        if len(value) < 6:
            raise serializers.ValidationError("新密码至少6位")
        # 不做其他复杂校验，满足“位数以外不限制”
        return value

    def save(self, **kwargs):
        user = self.context['request'].user
        new_password = self.validated_data['new_password']
        user.set_password(new_password)
        user.save()
        return user


class CommentSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.username', read_only=True)
    avatar = serializers.CharField(source='user.profile.avatar', read_only=True)
    time = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'name', 'avatar', 'content', 'time']
        read_only_fields = ['id', 'name', 'avatar', 'time']

    def get_time(self, obj):
        """格式化时间为友好显示"""
        now = timezone.now()
        diff = now - obj.created_at
        
        if diff.days == 0:
            # 今天
            return obj.created_at.strftime("今天 %H:%M")
        elif diff.days == 1:
            # 昨天
            return obj.created_at.strftime("昨天 %H:%M")
        elif diff.days < 7:
            # 一周内
            return obj.created_at.strftime("%A %H:%M")
        else:
            # 超过一周
            return obj.created_at.strftime("%Y-%m-%d %H:%M")


class PostSerializer(serializers.ModelSerializer):
    avatar = serializers.CharField(source='user.profile.avatar', read_only=True)
    nickname = serializers.CharField(source='user.username', read_only=True)
    time = serializers.SerializerMethodField(read_only=True)
    likes = serializers.IntegerField(source='likes_count', read_only=True)
    comments = serializers.IntegerField(source='comments_count', read_only=True)
    liked = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'avatar', 'nickname', 'time', 'text', 'type', 'media', 'likes', 'comments', 'liked']
        read_only_fields = ['id', 'avatar', 'nickname', 'time', 'likes', 'comments', 'liked']

    def get_time(self, obj):
        """格式化时间为友好显示"""
        now = timezone.now()
        diff = now - obj.created_at
        
        if diff.days == 0:
            # 今天
            return obj.created_at.strftime("今天 %H:%M")
        elif diff.days == 1:
            # 昨天
            return obj.created_at.strftime("昨天 %H:%M")
        elif diff.days < 7:
            # 一周内
            return obj.created_at.strftime("%A %H:%M")
        else:
            # 超过一周
            return obj.created_at.strftime("%Y-%m-%d %H:%M")

    def get_liked(self, obj):
        """检查当前用户是否已点赞该动态"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Like.objects.filter(user=request.user, post=obj).exists()
        return False


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['user', 'post']


class CreatePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['text', 'type', 'media']


class CreateCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['content']