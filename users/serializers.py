from rest_framework.serializers import ModelSerializer
from .models import User
from medias.serializers import PhotoSerializer
from medias.models import Photo


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = (
            "name",
            "avatar",
            "username",
        )


class PrivateUserSerializer(ModelSerializer):
    class Meta:
        model = User
        exclude = (
            "password",
            "is_superuser",
            "id",
            "is_staff",
            "is_active",
            "first_name",
            "last_name",
            "groups",
            "user_permissions",
        )


class UserPhotosSerializer(ModelSerializer):
    photos = PhotoSerializer(many=True, read_only=True)

    class Meta:
        model = Photo
        fields = "__all__"
