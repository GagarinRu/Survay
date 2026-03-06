from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

from base.models import NULLABLE, BaseModel

User = get_user_model()


class Survay(BaseModel):
    """Опрос."""

    title = models.CharField("название опроса", max_length=500)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_survays",
        verbose_name="автор",
    )

    class Meta:
        verbose_name = "опрос"
        verbose_name_plural = "опросы"
        ordering = ["-created"]

    def __str__(self):
        return self.title


class Question(BaseModel):
    """Вопрос в опросе."""

    survay = models.ForeignKey(
        Survay, on_delete=models.CASCADE, related_name="questions", verbose_name="опрос"
    )
    title = models.CharField("текст вопроса", max_length=1000)
    order = models.PositiveIntegerField(
        verbose_name="порядок",
        default=0,
        validators=[
            MinValueValidator(1, message="Порядок должен быть >= 1"),
            MaxValueValidator(15, message="Порядок должен быть <= 15"),
        ],
    )

    class Meta:
        verbose_name = "вопрос"
        verbose_name_plural = "вопросы"
        ordering = ["order"]

    def __str__(self):
        return self.title


class AnswerOption(BaseModel):
    """Вариант ответа на вопрос."""

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="answer_options",
        verbose_name="вопрос",
    )
    title = models.CharField("текст варианта", max_length=500)
    order = models.PositiveIntegerField(
        verbose_name="порядок",
        default=1,
        validators=[
            MinValueValidator(1, message="Порядок должен быть >= 1"),
            MaxValueValidator(5, message="Порядок должен быть <= 5"),
        ],
    )

    class Meta:
        verbose_name = "вариант ответа"
        verbose_name_plural = "варианты ответов"
        ordering = ["order"]

    def __str__(self):
        return self.title


class UserAnswer(BaseModel):
    """Ответ пользователя на вопрос."""

    username = models.CharField("имя пользователя", max_length=200, db_index=True)
    survay = models.ForeignKey(
        Survay,
        on_delete=models.CASCADE,
        related_name="user_answers",
        verbose_name="опрос",
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="user_answers",
        verbose_name="вопрос",
    )
    answer_option = models.ForeignKey(
        AnswerOption,
        on_delete=models.CASCADE,
        related_name="user_selections",
        verbose_name="выбранный вариант",
    )
    started_at = models.DateTimeField("время начала", **NULLABLE)
    answered_at = models.DateTimeField("время ответа", auto_now=True)

    class Meta:
        verbose_name = "ответ пользователя"
        verbose_name_plural = "ответы пользователей"
        indexes = [
            models.Index(fields=["survay", "username"]),
            models.Index(fields=["survay", "username", "question"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["username", "question"], name="unique_user_question"
            ),
        ]

    def __str__(self):
        return f"{self.username} - {self.question.title[:30]}"
