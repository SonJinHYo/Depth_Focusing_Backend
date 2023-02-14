import numpy as np
import requests
import os

from django.conf import settings

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.response import Response
from rest_framework import status

from users import serializers
from users.models import User
from .models import Photo
from .serializers import PhotoSerializer
from .segmentation import predict_segmentation, draw_panoptic_segmentation
from .bluring_img import predit_depth, bluring_img


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
        return Response(status=status.HTTP_200_OK)


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
        return Response(
            {"uploadURL": result.get("uploadURL")},
            status=status.HTTP_200_OK,
        )


class GetSegmentation(APIView):
    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise NotFound

    def post(self, request):
        photo = Photo.objects.get(file=request.data["file"])
        serializer = PhotoSerializer(photo)
        pk = serializer.data["pk"]
        img_url = serializer.data["file"]
        segmentation, segmentation_info, model = predict_segmentation(img_url)
        draw_panoptic_segmentation(model, segmentation, segmentation_info, pk)

        # 프로토타입
        labels_len = len(segmentation_info)

        seg_arr = np.array(segmentation)
        np.save(f"tmp/seg_arr_{pk}", seg_arr)

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
            files={"file": open(f"tmp/segmentation_{pk}.png", "rb")},
        )
        result = r.json().get("result")
        seg_image_url = result.get("variants")
        print(f"seg_image_url: {seg_image_url}")

        serializer = PhotoSerializer(
            photo,
            data={
                "seg_file": seg_image_url[0],
                "labels_len": labels_len,
            },
            partial=True,
        )
        if serializer.is_valid():
            photo = serializer.save()
            serializer = PhotoSerializer(photo)
            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )


class GetBlurImage(APIView):
    def post(self, request):
        photo = Photo.objects.get(seg_file=request.data["seg_file"])
        serializer = PhotoSerializer(photo)
        pk = serializer.data["pk"]
        check_labels = request.data["check_labels"]["check_labels"]
        strength = request.data["strength"]
        size = request.data["blur_size"]
        split = request.data["depth_split"]
        label = check_labels.index(True)
        img_url = serializer.data["file"]

        depth_map = predit_depth(img_url)
        segmentation = np.load(f"tmp/seg_arr_{pk}.npy")
        np.save(f"tmp/depth_map_{pk}", depth_map)

        bluring_img(
            img_url,
            label,
            segmentation,
            depth_map,
            pk,
            strength,
            split,
            size=size * 2 + 1,
        )

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
            files={"file": open(f"tmp/blured_image_{pk}.png", "rb")},
        )
        result = r.json().get("result")
        blured_image_url = result.get("variants")
        print(blured_image_url)

        serializer = PhotoSerializer(
            photo,
            data={"blured_file": blured_image_url[0]},
            partial=True,
        )

        os.remove(f"tmp/segmentation_{pk}.png")
        os.remove(f"tmp/blured_image_{pk}.png")

        if serializer.is_valid():
            print("seralizer ok")
            photo = serializer.save()
            serializer = PhotoSerializer(photo)
            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )


class GetBlurImageAgain(APIView):
    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise NotFound

    def post(self, request):
        photo = Photo.objects.get(seg_file=request.data["seg_file"])
        serializer = PhotoSerializer(photo)
        pk = serializer.data["pk"]
        check_labels = request.data["check_labels"]["check_labels"]
        strength = request.data["strength"]
        size = request.data["blur_size"]
        split = request.data["depth_split"]
        label = check_labels.index(True)
        img_url = serializer.data["file"]
        depth_map = np.load(f"tmp/depth_map_{pk}.npy")
        segmentation = np.load(f"tmp/seg_arr_{pk}.npy")
        bluring_img(
            img_url,
            label,
            segmentation,
            depth_map,
            pk,
            strength,
            split,
            size=size * 2 + 1,
        )

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
            files={"file": open(f"tmp/blured_image_{pk}.png", "rb")},
        )
        result = r.json().get("result")
        blured_image_url = result.get("variants")
        print(blured_image_url)

        serializer = PhotoSerializer(
            photo,
            data={"blured_file": blured_image_url[0]},
            partial=True,
        )

        os.remove(f"tmp/blured_image_{pk}.png")

        if serializer.is_valid():
            print("seralizer ok")
            photo = serializer.save()
            serializer = PhotoSerializer(photo)
            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )
