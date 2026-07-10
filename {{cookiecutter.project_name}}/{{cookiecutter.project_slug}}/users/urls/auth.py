from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

app_name = "auth"

urlpatterns = [
    path("jwt/login/", TokenObtainPairView.as_view(), name="login"),
    path("jwt/refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("jwt/verify/", TokenVerifyView.as_view(), name="verify"),
]
