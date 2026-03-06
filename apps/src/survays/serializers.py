from rest_framework import serializers
from django.db.models import Count, Min, Max

from survays.models import AnswerOption, Question, Survay, UserAnswer


class AnswerOptionSerializer(serializers.ModelSerializer):
    """Сериализатор варианта ответа."""

    class Meta:
        model = AnswerOption
        fields = ("id", "title", "order", "question")
        read_only_fields = ("id",)


class AnswerOptionCreateSerializer(serializers.Serializer):
    """Сериализатор создания варианта ответа."""

    title = serializers.CharField(max_length=500)
    order = serializers.IntegerField(default=0, max_value=5)


class QuestionSerializer(serializers.ModelSerializer):
    """Сериализатор вопроса."""

    answer_options = AnswerOptionSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ("id", "title", "order", "survay", "answer_options")
        read_only_fields = ("id", "survay")


class QuestionCreateSerializer(serializers.Serializer):
    """Сериализатор создания вопроса."""

    title = serializers.CharField(max_length=1000)
    order = serializers.IntegerField(default=0, max_value=15)
    answer_options = AnswerOptionCreateSerializer(many=True, required=False)


class SurvaySerializer(serializers.ModelSerializer):
    """Сериализатор опроса."""

    questions = QuestionSerializer(many=True, read_only=True)
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Survay
        fields = ("id", "title", "author", "questions", "created")
        read_only_fields = ("author", "created")


class SurvayCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания опроса."""

    questions = QuestionCreateSerializer(many=True, required=False)

    class Meta:
        model = Survay
        fields = ("id", "title", "author", "questions", "created")
        read_only_fields = ("author", "created")

    def create(self, validated_data):
        questions = validated_data.pop("questions", [])
        survay = Survay.objects.create(**validated_data)

        for q in questions:
            options = q.pop("answer_options", [])
            question = Question.objects.create(survay=survay, **q)
            AnswerOption.objects.bulk_create(
                [AnswerOption(question=question, **o) for o in options]
            )
        return survay


class AnswerOptionForQuestionSerializer(serializers.ModelSerializer):
    """Упрощенный сериализатор варианта ответа."""

    class Meta:
        model = AnswerOption
        fields = ("id", "title", "order")


class QuestionDetailSerializer(serializers.ModelSerializer):
    """Детальный сериализатор вопроса."""

    answer_options = AnswerOptionForQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ("id", "title", "order", "answer_options")


class AnswerSubmitSerializer(serializers.Serializer):
    """Сериализатор отправки ответа."""

    username = serializers.CharField(
        required=False, default="anonymous", max_length=200
    )
    question_id = serializers.IntegerField()
    answer_option_id = serializers.IntegerField()


class MessageSerializer(serializers.Serializer):
    """Сериализатор сообщения."""

    message = serializers.CharField()


class SurvayStatsSerializer(serializers.ModelSerializer):
    """Сериализатор статистики опроса."""

    total_responses = serializers.SerializerMethodField()
    avg_duration_seconds = serializers.SerializerMethodField()
    questions = serializers.SerializerMethodField()

    class Meta:
        model = Survay
        fields = ("id", "title", "total_responses", "avg_duration_seconds", "questions")

    def get_total_responses(self, obj):
        return (
            UserAnswer.objects.filter(survay=obj).values("username").distinct().count()
        )

    def get_avg_duration_seconds(self, obj):
        users = (
            UserAnswer.objects.filter(survay=obj, started_at__isnull=False)
            .values("username")
            .annotate(start=Min("started_at"), end=Max("answered_at"))
        )
        durations = [
            (u["end"] - u["start"]).total_seconds()
            for u in users
            if u["start"] and u["end"]
        ]
        return round(sum(durations) / len(durations), 2) if durations else 0

    def get_questions(self, obj):
        questions = obj.questions.annotate(
            total_answers_count=Count("user_answers")
        ).order_by("order")
        popular_answers_qs = (
            UserAnswer.objects.filter(question__survay=obj)
            .values("question_id", "answer_option__title")
            .annotate(count=Count("id"))
            .order_by("question_id", "-count")
        )
        popular_by_question = {}
        for item in popular_answers_qs:
            q_id = item["question_id"]
            if q_id not in popular_by_question:
                popular_by_question[q_id] = []
            if len(popular_by_question[q_id]) < 3:
                popular_by_question[q_id].append(
                    {
                        "answer_option__title": item["answer_option__title"],
                        "count": item["count"],
                    }
                )
        return [
            {
                "question_id": question.id,
                "question_title": question.title[:50],
                "total_answers": question.total_answers_count,
                "popular_answers": popular_by_question.get(question.id, []),
            }
            for question in questions
        ]
