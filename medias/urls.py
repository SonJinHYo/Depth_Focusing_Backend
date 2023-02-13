from django.urls import path
from .views import PhotoDetail, GetUploadURL, GetSegmentation, GetBlurImage, GetDepthMap

urlpatterns = [
    path("photos/<int:pk>", PhotoDetail.as_view()),
    path("photos/get-url", GetUploadURL.as_view()),
    path("photos/get-segmentation", GetSegmentation.as_view()),
    path("photos/get-blurimage", GetBlurImage.as_view()),
    path("photos/get-depthmap", GetDepthMap.as_view()),
]
