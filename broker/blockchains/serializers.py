from django.core.validators import RegexValidator
from django_uuid7 import UUID7SerializerField
from rest_framework_json_api import serializers
from django.contrib.auth import get_user_model
import uuid_utils as uuid
from .models import Wallet, TX


class WalletSerializer(serializers.ModelSerializer):
    id = UUID7SerializerField(
        read_only=True, default=lambda: str(uuid.uuid7())
    )  # @TODO: Fix the broken uuid implementation for the django_uuid7
    user = serializers.PrimaryKeyRelatedField(queryset=get_user_model().objects.all())
    label = serializers.CharField(max_length=255)
    balance = serializers.DecimalField(max_digits=26, decimal_places=18)
    status = serializers.ChoiceField(choices=Wallet.WalletStatus.choices)

    class Meta:
        model = Wallet
        fields = ("id", "user", "label", "balance", "status")


class TXSerializer(serializers.ModelSerializer):
    id = UUID7SerializerField(
        read_only=True, default=lambda: str(uuid.uuid7())
    )  # @TODO: Fix the broken uuid implemetation
    txid = serializers.CharField(
        max_length=100,
        validators=[
            RegexValidator(r"^[xa-fA-F0-9-]{64,100}$"),
        ],
    )
    wallet = serializers.PrimaryKeyRelatedField(queryset=Wallet.objects.all())
    amount = serializers.DecimalField(max_digits=26, decimal_places=18)

    class Meta:
        model = TX
        fields = ("id", "wallet", "txid", "amount")
