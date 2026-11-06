import factory

from {{cookiecutter.project_slug}}.users.models import BaseUser


class BaseUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BaseUser
        skip_postgeneration_save = True

{%- if cookiecutter.user_login_field == "username" %}
    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.Sequence(lambda n: f"user{n}@example.com")
{%- else %}
    email = factory.Sequence(lambda n: f"user{n}@example.com")
{%- endif %}
{%- if cookiecutter.use_otp_login == "y" %}
    phone = factory.Sequence(lambda n: f"98913{n:07d}")
{%- endif %}

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        password = kwargs.pop("password", "Password1!x")
        return model_class.objects.create_user(password=password, **kwargs)
