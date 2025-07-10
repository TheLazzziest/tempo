import factory
import uuid_utils as uuid


class WalletFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "blockchains.Wallet"
        django_get_or_create = ("id", "label", "balance")

    id = factory.Sequence(
        lambda n: uuid.uuid7(n)
    )  # @TODO: Implement custom sequence for uuid7
    label = factory.Sequence(lambda n: f"Wallet {n}")
    balance = factory.Faker("pydecimal", left_digits=8, right_digits=18, positive=True)

    @factory.post_generation
    def transactions(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for _ in range(extracted):
                TXFactory(wallet_id=self)


class TXFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "blockchains.TX"
        django_get_or_create = ("id", "txid", "amount")

    id = factory.Sequence(lambda n: uuid.uuid7(n))
    wallet = factory.SubFactory(WalletFactory)
    txid = factory.Faker("sha256")
    amount = factory.Faker("pydecimal", left_digits=7, right_digits=18, positive=True)
