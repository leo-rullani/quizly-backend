from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.urls import path
from .views import RegistrationView, CookieTokenObtainPairView, CookieRefreshView

urlpatterns = [
    path("registration/", RegistrationView.as_view(), name="api-registration"),
    path("token/", CookieTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", CookieRefreshView.as_view(), name="token_refresh"),
]