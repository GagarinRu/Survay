from django.contrib import admin
from survays.models import AnswerOption, Question, Survay


@admin.register(Survay)
class SurvayAdmin(admin.ModelAdmin):
    pass


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    pass


@admin.register(AnswerOption)
class AnswerOptionAdmin(admin.ModelAdmin):
    pass
