from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated


from .serializers import VideoSerializer,VideoListSerializer, RegisterSerializer, QuestionSerializer
from .services.video_service import VideoService
from .services.vector_service import VectorService
from .services.rag_service import RAGService
from .models import Video, Question
# Create your views here.

class VideoViewSet(ModelViewSet):
    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "list":
            return VideoListSerializer

        return VideoSerializer
    
    def get_queryset(self):
        queryset = Video.objects.filter(user=self.request.user).order_by("-created_at")

        status_filter = self.request.query_params.get('status')

        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset

    def perform_create(self, serializer):
        video = serializer.save(user=self.request.user)

        try:
            VideoService().process_video(video)
        except ValueError as e:
            raise serializers.ValidationError({
                "error": str(e)
            })

    def destroy(self, request, *args, **kwargs):
        video = self.get_object()

        vector_service = VectorService()
        vector_service.delete_video_vectors(video.id)

        return super().destroy(request, *args, **kwargs)

class QuestionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        questions = Question.objects.filter(
            video__user=request.user
        ).order_by('-created_at')

        video_id = request.query_params.get("video")

        if video_id:
            questions = questions.filter(video_id=video_id)

        serializer = QuestionSerializer(
            questions,
            many=True
        )

        return Response(serializer.data)

    def post(self, request):
        serializer = QuestionSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        video = serializer.validated_data["video"]
        question = serializer.validated_data["question"]

        if video.user != request.user:
            return Response(
                {"error": "Video not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        vector_service = VectorService()
        vector_store = vector_service.get_vector_store()

        rag_service = RAGService()
        rag_chain = rag_service.build_rag_chain(
            vector_store,
            video.id
            )

        answer = rag_service.ask_question(
            rag_chain,
            question
        )

        question_obj = serializer.save(answer=answer)

        return Response(
            QuestionSerializer(question_obj).data,
            status=status.HTTP_201_CREATED
        )

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