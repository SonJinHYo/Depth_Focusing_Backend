from django.conf import settings
import requests

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from users import serializers
from users.models import User
from .models import Photo
from .serializers import PhotoSerializer
from .segmentation import predict_segmentation, draw_panoptic_segmentation


class PhotoDetail(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Photo.objects.get(pk=pk)
        except Photo.DoesNotExist:
            raise NotFound

    def delete(self, request, pk):
        photo = self.get_object(pk)
        if photo.user and photo.user != request.user:
            raise PermissionDenied
        photo.delete()
        return Response(status=HTTP_200_OK)


class GetUploadURL(APIView):
    def post(self, request):
        url = f"https://api.cloudflare.com/client/v4/accounts/{settings.CF_ID}/images/v2/direct_upload"
        one_time_url = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {settings.CF_TOKEN}",
            },
        )

        one_time_url = one_time_url.json()
        # result.get("uploadURL") : 유저에게 할당해주는 이미지 업로드용 url
        result = one_time_url.get("result")
        return Response({"uploadURL": result.get("uploadURL")})


# 우석님 파트
class GetDeepLearningImage(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise NotFound

    def post(self, request):
        user = self.get_object(1)
        photo = Photo.objects.get(pk=request.data["pk"])
        serializer = PhotoSerializer(photo)
        img_url = serializer.data["file"]
        segmentation, segmentation_info, model = predict_segmentation(img_url)
        draw_panoptic_segmentation(model, segmentation, segmentation_info)

        one_time_url = requests.post(
            f"https://api.cloudflare.com/client/v4/accounts/{settings.CF_ID}/images/v2/direct_upload",
            headers={
                "Authorization": f"Bearer {settings.CF_TOKEN}",
            },
        )

        one_time_url = one_time_url.json()
        result = one_time_url.get("result")

        r = requests.post(
            result.get("uploadURL"),
            files={"file": open("segmentation.png", "rb")},
        )
        result = r.json().get("result")
        seg_image_url = result.get("variants")

        serializer = PhotoSerializer(
            photo,
            {"seg_file": seg_image_url},
            partial=True,
        )

        if serializer.is_valid():
            photo = serializer.save()
            serializer = PhotoSerializer(photo)
            print("save")

        return Response({"uploadURL": result.get("uploadURL")})


class GetBlurImage(APIView):
    def post(self, request):
        "라벨번호, segmentation 이미지, depthmap 이미지 를 가지고 블러이미지를 만들어서 반환"

        pass
