from rest_framework import status
from rest_framework.exceptions import APIException
from django.utils.translation import gettext_lazy as _


class UnprocessableEntity(APIException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = _("Content is not processable")
    default_code = "unprocessable_entity"
