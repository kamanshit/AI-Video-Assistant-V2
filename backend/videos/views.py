from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated


from .serializers import VideoSerializer, RegisterSerializer
from .models import Video
# Create your views here.

class VideoViewSet(ModelViewSet):
    queryset         = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user = self.request.user)

class RegisterAPIView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data = request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                'message': 'User created successfully'
            },
            status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class LoginAPIView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(
            username=username,
            password=password
        )

        if user is not None:
            token, created = Token.objects.get_or_create(
                user = user
            )

            return Response({
                'token': token.key
            })

        return Response(
            {
                'error': 'Invalid username or password'
            },
            status=status.HTTP_401_UNAUTHORIZED
        )