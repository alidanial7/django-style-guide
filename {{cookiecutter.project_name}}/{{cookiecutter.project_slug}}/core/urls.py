from django.urls import path

from .apis import HealthApi

urlpatterns = [
    path("health/", HealthApi.as_view(), name="health"),
]
