from rest_framework import serializers
from .models import Video
from django.contrib.auth.models import User

class VideoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Video

        fields = [
            'id',
            'user',
            'title',
            'source',
            'file',
            'language',
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

    def validate_language(self, value):
        if value.lower() != "english":
            raise serializers.ValidationError(
                "Only English is currently supported."
            )

        return value.lower()

    def validate(self, attrs):
        source = attrs.get('source')
        file = attrs.get('file')

        if not source and not file:
            raise serializers.ValidationError(
                "Provide either a video source URL or a video file."
            )

        return attrs

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



