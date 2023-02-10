from django.urls import path
from .views import PhotoDetail, GetUploadURL, GetDeepLearningImage, GetBlurImage

urlpatterns = [
    path("photos/<int:pk>", PhotoDetail.as_view()),
    path("photos/get-url", GetUploadURL.as_view()),
    path("photos/asdasd", GetDeepLearningImage.as_view()),
    path("photos/bbbb", GetBlurImage.as_view()),
]
