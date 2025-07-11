from django.core.exceptions import ValidationError
from rest_framework import permissions, mixins, viewsets
from rest_framework_json_api import views, exceptions as exceptions_extensions
from django.db.models import ProtectedError

from broker.exceptions import UnprocessableEntity

from .models import Wallet, TX
from .serializers import WalletSerializer, TXSerializer
from .perimssions import IsWalletActive, IsWalletOwner


class WalletViewSet(views.ModelViewSet):
    """
    Handles Wallet-related operations.
    """

    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated, IsWalletOwner]

    def perform_destroy(self, instance):
        try:
            super().perform_destroy(instance)
        except ProtectedError as e:
            raise exceptions_extensions.Conflict(e.args[0]) from e
        except ValidationError as e:
            raise UnprocessableEntity(e.args[0]) from e


class TXViewSet(
    views.AutoPrefetchMixin,
    views.PreloadIncludesMixin,
    views.RelatedMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    Handles TX-related operations.
    """

    queryset = TX.objects.all()
    serializer_class = TXSerializer

    def get_permissions(self):
        if self.action in ["create"]:
            return [
                permission()
                for permission in self.permission_classes + [IsWalletActive]
            ]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        try:
            super().perform_create(serializer)
        except ValidationError as e:
            # Use case:
            # * When a wallet balance is attempted to decrease bellow 0
            # * When a wallet balance exceeds the max value
            raise UnprocessableEntity(e.args[0]) from e
