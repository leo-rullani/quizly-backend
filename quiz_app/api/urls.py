"""URL routes for the quiz API."""

from django.urls import path

from .views import CreateQuizView, QuizDetailView, QuizListView

urlpatterns = [
    path("createQuiz/", CreateQuizView.as_view(), name="create-quiz"),
    path("quizzes/", QuizListView.as_view(), name="quiz-list"),
    path("quizzes/<int:pk>/", QuizDetailView.as_view(), name="quiz-detail"),
]