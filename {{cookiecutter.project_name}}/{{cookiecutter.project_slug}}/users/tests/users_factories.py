import factory

from {{cookiecutter.project_slug}}.users.models import BaseUser, Profile


class BaseUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BaseUser

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "Password1!x")


class ProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Profile

    user = factory.SubFactory(BaseUserFactory)
    bio = factory.Faker("sentence")
