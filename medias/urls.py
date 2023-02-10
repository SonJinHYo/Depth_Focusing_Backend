from django.urls import path
from .views import PhotoDetail, GetUploadURL, GetSegmentation, GetBlurImage

urlpatterns = [
    path("photos/<int:pk>", PhotoDetail.as_view()),
    path("photos/get-url", GetUploadURL.as_view()),
    path("photos/GetSegmentation", GetSegmentation.as_view()),
    path("photos/GetBlurImage", GetBlurImage.as_view()),
]
