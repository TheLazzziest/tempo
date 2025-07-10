import pytest
from django_uuid7 import uuid7
from faker import Faker
from faker.providers import DynamicProvider
from rest_framework.test import APIClient
from pytest_django.lazy_django import skip_if_no_django

from .types import User
from .users.test.factories import UserFactory

# Custom Faker Providers
uuid7_provider = DynamicProvider(
    provider_name="uuid7",
    generator=uuid7,
)

fake = Faker()
fake.add_provider(uuid7_provider)


# Ensures pytest waits for the database to load
# https://pytest-django.readthedocs.io/en/latest/faq.html#how-can-i-give-database-access-to-all-my-tests-without-the-django-db-marker
@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


@pytest.fixture()
def default_user(db) -> User:
    return UserFactory()


@pytest.fixture()
def authorized_api_client(default_user: User) -> APIClient:
    skip_if_no_django()

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Token {default_user.auth_token}")
    return client
