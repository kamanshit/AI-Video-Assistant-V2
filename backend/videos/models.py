from django.db import models
from django.contrib.auth.models import User


class Video(models.Model):

    STATUS_CHOICES = [
        ("uploaded", "Uploaded"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="videos"
    )

    title = models.CharField(max_length=255)
    source = models.URLField(blank=True, null=True)
    file = models.FileField(upload_to="videos/", blank=True, null=True)

    language = models.CharField(
    max_length=20,
    default="english"
    )
    transcript = models.TextField(blank=True, null=True)

    
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default="uploaded"
    )


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title