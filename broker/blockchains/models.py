from decimal import Decimal
from django.core.validators import MinValueValidator, RegexValidator
from django_uuid7 import UUID7Field
from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
import uuid_utils as uuid


class TXManager(models.Manager):
    def create(self, wallet: "Wallet", **kwargs):
        with transaction.atomic():
            # Lock the related wallet row to prevent race conditions during the update.
            wallet = Wallet.objects.select_for_update().get(pk=wallet.id)
            # If the transaction is new (being created), just add its amount to the wallet's balance.
            wallet.balance += kwargs.get("amount")
            wallet.save()
            return super().create(wallet=wallet, **kwargs)


class Wallet(models.Model):
    class WalletStatus(models.TextChoices):
        ACTIVE = "A", _("Active")
        DISABLED = "D", _("Disabled")
        SUSPENDED = "S", _("Suspended")

    # UUID7 helps to improve performance of a clustered index
    id = UUID7Field(
        primary_key=True, default=lambda: str(uuid.uuid7())
    )  # the field is locked to uuid module
    user = models.ForeignKey("users.User", editable=False, on_delete=models.PROTECT)
    label = models.CharField(
        max_length=255, db_comment="A human-readable name for the wallet."
    )
    balance = models.DecimalField(
        max_digits=26,
        decimal_places=18,
        validators=[
            MinValueValidator(Decimal("0.0"), message="Balance cannot be less than 0")
        ],
        db_comment="The current balance of the wallet, derived from the sum of its transactions.",
    )
    status = models.CharField(
        choices=WalletStatus.choices,
        default=WalletStatus.ACTIVE,
        max_length=1,
        db_comment="The current status of the wallet.",
    )

    def __str__(self):
        return self.label

    def __repr__(self):
        return f"<Wallet: {self.id} - {self.label}: {self.balance}>"

    class Meta:
        ordering = ("id",)


@receiver(pre_save, sender=Wallet)
def ensure_balance_is_positive(sender, instance: Wallet, *args, **kwargs):
    instance.full_clean()


class TX(models.Model):
    id = UUID7Field(
        primary_key=True, default=lambda: str(uuid.uuid7())
    )  # the field is locked to uuid module
    wallet = models.ForeignKey(Wallet, on_delete=models.PROTECT)
    txid = models.CharField(
        max_length=100,
        validators=[RegexValidator(r"^[xa-fA-F0-9-]{64,100}$")],
        unique=True,
        editable=False,
        db_comment="The unique transaction identifier (hash) from the blockchain.",
    )
    amount = models.DecimalField(
        max_digits=26,
        decimal_places=18,
        editable=False,
        db_comment="The value of the transaction, can be positive or negative.",
    )

    objects = TXManager()

    def __str__(self):
        return f"{self.txid}: {self.amount}"

    def __repr__(self):
        return f"<TX: {self.id} - {self.txid}: {self.amount}>"

    class Meta:
        ordering = ("-id",)
