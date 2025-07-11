from typing import TypeVar
from django.contrib.auth.models import AbstractUser


User = TypeVar("User", bound=AbstractUser)
