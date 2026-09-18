from rest_framework import serializers
from .models import Video
from django.contrib.auth.models import User

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Video
        fields = [
                'id',
                'user',
                'title',
                'source',
                'file',
                'transcript',
                'status',
                'created_at',
                'updated_at',
        ]
        read_only_fields = [
                'id',
                'user',
                'transcript',
                'status',
                'created_at',
                'updated_at',
        ]

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ['username', 'password']
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }


    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user



