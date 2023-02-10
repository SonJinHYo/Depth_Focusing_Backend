from django.db import models
from django.contrib.postgres.fields import ArrayField


class Photo(models.Model):
    file = models.URLField()
    seg_file = models.URLField(default="")
    blured_file = models.URLField(default="")
    labels_len = models.PositiveIntegerField(default=1)
    segmentation = models.URLField(default="")
    #     models.IntegerField(),
    #     null=True,
    #     blank=True,
    # )
    description = models.CharField(
        max_length=140,
    )
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="photos",
    )

    def __str__(self):
        return "Photo File"
