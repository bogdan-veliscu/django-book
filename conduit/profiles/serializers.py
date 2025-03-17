import logging

from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from conduit.profiles.models import User

logger = logging.getLogger(__name__)


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    token = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'name', 'password', 'token')

    def get_token(self, obj):
        refresh = RefreshToken.for_user(obj)
        return str(refresh.access_token)

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password']
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class ProfileSerializer(serializers.ModelSerializer):
    following = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('username', 'bio', 'image', 'following')
        read_only_fields = ('username',)

    def get_following(self, instance):
        request = self.context.get('request', None)
        if request is None or not request.user.is_authenticated:
            return False
        return request.user.following.filter(pk=instance.pk).exists()

    def update(self, instance, validated_data):
        logger.info(f" # UPDATE : bio: {instance.bio}, image: {instance.image}")
        logger.info(f"instance: {instance}, validated_data: {validated_data}")

        for key, value in validated_data.items():
            logger.info(f"key: {key}, value: {value}")
            if key == "password":
                instance.set_password(value)
            elif key == "bio":  # Add this line to handle the 'bio' field
                setattr(instance, key, value)
            else:
                setattr(instance, key, value)
        logger.info(f" # after bio: {instance.bio}, image: {instance.image}")

        instance.save()
        return instance
