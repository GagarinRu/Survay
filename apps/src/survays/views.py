from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework import viewsets, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_spectacular.utils import extend_schema, OpenApiParameter

from survays.models import Survay, Question, AnswerOption, UserAnswer
from survays.serializers import (
    SurvaySerializer,
    QuestionSerializer,
    AnswerOptionSerializer,
    SurvayCreateSerializer,
    QuestionDetailSerializer,
    AnswerSubmitSerializer,
    SurvayStatsSerializer,
    MessageSerializer,
)


@extend_schema(tags=["Survays"])
class SurvayViewSet(viewsets.ModelViewSet):
    """ViewSet для опросов."""

    queryset = Survay.objects.all()

    def get_permissions(self):
        if self.action in [
            "list",
            "retrieve",
            "next_question",
            "submit_answer",
            "get_stats",
        ]:
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action == "create":
            return SurvayCreateSerializer
        return SurvaySerializer

    @extend_schema(
        parameters=[
            OpenApiParameter("username", str, required=False, default="anonymous")
        ],
        responses={200: QuestionDetailSerializer, 200: MessageSerializer},  # noqa
    )
    @action(detail=True, methods=["get"], url_path="next-question")
    def next_question(self, request, pk=None):
        """Возвращает следующий вопрос опроса."""
        survay = self.get_object()
        username = request.query_params.get("username", "anonymous")
        answered = UserAnswer.objects.filter(username=username, survay=survay)
        next_question = (
            Question.objects.filter(survay=survay)
            .exclude(id__in=answered.values_list("question_id", flat=True))
            .order_by("order")
            .first()
        )
        if not answered.exists():
            request.session[f"survey_start_{survay.id}"] = timezone.now().isoformat()
        if not next_question:
            return Response(
                MessageSerializer({"message": "Все вопросы опроса отвечены"}).data
            )
        return Response(QuestionDetailSerializer(next_question).data)

    @extend_schema(
        request=AnswerSubmitSerializer, responses={200: AnswerSubmitSerializer}
    )
    @action(detail=True, methods=["post"], url_path="answer")
    def submit_answer(self, request, pk=None):
        """Сохраняет ответ пользователя."""
        survay = self.get_object()
        serializer = AnswerSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        username = data.get("username", "anonymous")
        started_at = request.session.pop(f"survey_start_{survay.id}", None)
        if started_at:
            started_at = parse_datetime(started_at)
        UserAnswer.objects.update_or_create(
            username=username,
            question_id=data["question_id"],
            defaults={
                "answer_option_id": data["answer_option_id"],
                "survay": survay,
                "started_at": started_at,
            },
        )
        return Response(serializer.data)

    @extend_schema(responses={200: SurvayStatsSerializer})
    @action(detail=True, methods=["get"], url_path="stats")
    def get_stats(self, request, pk=None):
        """Возвращает статистику опроса."""
        survay = self.get_object()
        return Response(SurvayStatsSerializer(survay).data)


@extend_schema(tags=["Questions"])
class QuestionViewSet(viewsets.ModelViewSet):
    """ViewSet для вопросов."""

    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if survay_id := self.request.query_params.get("survay_id"):
            qs = qs.filter(survay_id=survay_id)
        return qs

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        survay = Survay.objects.get(id=self.request.data["survay"])
        if survay.author != self.request.user:
            raise serializers.ValidationError("Только автор может добавлять вопросы")
        serializer.save(survay=survay)


@extend_schema(tags=["Answer Options"])
class AnswerOptionViewSet(viewsets.ModelViewSet):
    """ViewSet для вариантов ответов."""

    queryset = AnswerOption.objects.all()
    serializer_class = AnswerOptionSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if question_id := self.request.query_params.get("question_id"):
            qs = qs.filter(question_id=question_id)
        return qs

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        question = Question.objects.get(id=self.request.data["question"])
        if question.survay.author != self.request.user:
            raise serializers.ValidationError("Только автор может добавлять варианты")
        serializer.save(question=question)
