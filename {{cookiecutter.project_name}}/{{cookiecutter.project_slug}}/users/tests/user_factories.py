import factory

from {{cookiecutter.project_slug}}.users.models import BaseUser


class BaseUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BaseUser
        skip_postgeneration_save = True

    email = factory.Sequence(lambda n: f"user{n}@example.com")

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        password = kwargs.pop("password", "Password1!x")
        return model_class.objects.create_user(password=password, **kwargs)
