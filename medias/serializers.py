from rest_framework.serializers import ModelSerializer
from .models import Photo


class PhotoSerializer(ModelSerializer):
    class Meta:
        model = Photo
        fields = (
            "pk",
            "file",
            "seg_file",
            "blured_file",
            "description",
            "segmentation",
            "labels",
        )
