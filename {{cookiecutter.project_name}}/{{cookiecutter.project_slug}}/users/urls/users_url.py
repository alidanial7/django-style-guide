from django.urls import path

from {{cookiecutter.project_slug}}.users.apis.users import UsersProfileApi, UsersRegisterApi

app_name = "users"

urlpatterns = [
    path("register/", UsersRegisterApi.as_view(), name="register"),
    path("profile/", UsersProfileApi.as_view(), name="profile"),
]
