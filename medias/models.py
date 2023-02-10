from django.db import models


class Photo(models.Model):
    file = models.URLField()
    seg_file = models.URLField(default="")
    blured_file = models.URLField(default="")
    labels = models.JSONField(default=dict)
    segmentation = models.BinaryField()
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
