from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    first_name = models.CharField(
        max_length=150,
        editable=False,
    )
    last_name = models.CharField(
        max_length=150,
        editable=False,
    )

    name = models.CharField(
        max_length=20,
        default="",
    )

    # 프로필 사진
    avatar = models.URLField(blank=True)
