from django.urls import path, include
from rest_framework.routers import DefaultRouter

from survays.views import SurvayViewSet, QuestionViewSet, AnswerOptionViewSet

router = DefaultRouter()
router.register(r"survays", SurvayViewSet)
router.register(r"questions", QuestionViewSet)
router.register(r"options", AnswerOptionViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
