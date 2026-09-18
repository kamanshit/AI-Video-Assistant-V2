from django.db import models
from django.contrib.auth.models import User


class Video(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="videos"
    )

    title = models.CharField(max_length=255)
    source = models.URLField(blank=True, null=True)
    file = models.FileField(upload_to="videos/", blank=True, null=True)

    transcript = models.TextField(blank=True, null=True)

    status = models.CharField(
        max_length=50,
        default="uploaded"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title