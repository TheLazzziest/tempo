from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
import pytest

from broker.conftest import User

from ..models import TX, Wallet
from .factories import TXFactory, WalletFactory


@pytest.fixture
def wallet(default_user: User) -> Wallet:
    return WalletFactory.build(user=default_user)


@pytest.fixture
def transaction(wallet: Wallet) -> TX:
    return TXFactory.build(wallet=wallet)


@pytest.mark.django_db
def test_create_wallet_with_no_data_fails(authorized_api_client: APIClient):
    response = authorized_api_client.post(reverse("wallet-list"), {})
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_create_wallet_with_valid_data_succeeds(
    authorized_api_client: APIClient, default_user: User, wallet: Wallet
):
    response = authorized_api_client.post(
        reverse("wallet-list"),
        {
            "data": {
                "type": "Wallet",
                "attributes": {
                    "label": wallet.label,
                    "balance": wallet.balance,
                    "user": default_user.pk,
                    "status": wallet.status,
                },
            }
        },
    )
    assert response.status_code == status.HTTP_201_CREATED

    wallet = Wallet.objects.get(pk=response.data.get("id"))
    assert wallet.label == wallet.label
    assert wallet.balance == wallet.balance
    assert str(wallet.user.id) == default_user.id


@pytest.mark.django_db
def test_get_request_returns_a_given_wallet(
    authorized_api_client: APIClient, wallet: Wallet
):
    response = authorized_api_client.post(
        reverse("wallet-list"),
        {
            "data": {
                "type": "Wallet",
                "attributes": {
                    "label": wallet.label,
                    "balance": wallet.balance,
                    "user": wallet.user.pk,
                    "status": wallet.status,
                },
            }
        },
    )
    assert response.status_code == status.HTTP_201_CREATED

    wallet = Wallet.objects.get(pk=response.data.get("id"))
    response = authorized_api_client.get(
        reverse("wallet-detail", kwargs={"pk": wallet.pk})
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_put_request_updates_a_wallet(authorized_api_client: APIClient, wallet: Wallet):
    response = authorized_api_client.post(
        reverse("wallet-list"),
        {
            "data": {
                "type": "Wallet",
                "attributes": {
                    "label": wallet.label,
                    "balance": wallet.balance,
                    "user": wallet.user.pk,
                    "status": wallet.status,
                },
            }
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    wallet = Wallet.objects.get(pk=response.data.get("id"))

    new_label = "New Wallet Label"
    payload = {
        "data": {
            "type": "Wallet",
            "id": wallet.pk,
            "attributes": {"label": new_label},
        }
    }
    response = authorized_api_client.patch(
        reverse("wallet-detail", kwargs={"pk": wallet.pk}), payload
    )
    assert response.status_code == status.HTTP_200_OK

    updated_wallet = Wallet.objects.get(pk=wallet.id)
    assert updated_wallet.label == new_label


@pytest.mark.django_db
def test_delete_request_deletes_a_wallet_with_no_transactions(
    authorized_api_client: APIClient, wallet: Wallet
):
    response = authorized_api_client.post(
        reverse("wallet-list"),
        {
            "data": {
                "type": "Wallet",
                "attributes": {
                    "label": wallet.label,
                    "balance": wallet.balance,
                    "user": wallet.user.pk,
                    "status": wallet.status,
                },
            }
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    wallet = Wallet.objects.get(pk=response.data.get("id"))

    response = authorized_api_client.delete(
        reverse("wallet-detail", kwargs={"pk": wallet.pk})
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Wallet.objects.filter(pk=wallet.pk).exists()


@pytest.mark.django_db
def test_delete_request_fails_for_wallet_with_transactions(
    authorized_api_client: APIClient, wallet: Wallet, transaction: TX
):
    # Create the wallet
    response = authorized_api_client.post(
        reverse("wallet-list"),
        {
            "data": {
                "type": "Wallet",
                "attributes": {
                    "label": wallet.label,
                    "balance": wallet.balance,
                    "user": wallet.user.pk,
                    "status": wallet.status,
                },
            }
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    wallet = Wallet.objects.get(pk=response.data.get("id"))

    # Create a transaction for the wallet
    response = authorized_api_client.post(
        reverse("tx-list"),
        {
            "data": {
                "type": "TX",
                "attributes": {
                    "wallet": str(wallet.pk),
                    "txid": transaction.txid,
                    "amount": str(transaction.amount),
                },
            }
        },
    )
    assert response.status_code == status.HTTP_201_CREATED

    tx = TX.objects.get(pk=response.data.get("id"))
    assert tx.wallet == wallet
    assert tx.txid == transaction.txid
    assert tx.amount == transaction.amount

    # Attempt to delete the wallet
    response = authorized_api_client.delete(
        reverse("wallet-detail", kwargs={"pk": wallet.pk})
    )
    assert response.status_code == status.HTTP_409_CONFLICT
    assert Wallet.objects.filter(pk=wallet.pk).exists()


@pytest.mark.django_db
def test_create_transaction_with_no_data_fails(authorized_api_client: APIClient):
    response = authorized_api_client.post(reverse("tx-list"), {})
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_create_transaction_with_valid_data_succeeds(
    authorized_api_client: APIClient, wallet: Wallet
):
    # Create the wallet
    response = authorized_api_client.post(
        reverse("wallet-list"),
        {
            "data": {
                "type": "Wallet",
                "attributes": {
                    "label": wallet.label,
                    "balance": wallet.balance,
                    "user": wallet.user.pk,
                    "status": wallet.status,
                },
            }
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    wallet = Wallet.objects.get(pk=response.data.get("id"))

    # Use authorized_api_client instead of authorized_client
    response = authorized_api_client.post(
        reverse("tx-list"),
        {
            "data": {
                "type": "TX",
                "attributes": {
                    "wallet": wallet.id,
                    "txid": "F4184fc596403b9d638783cf57adfe4c75c605f6356fbc91338530e9831e9e16",
                    "amount": Decimal("10.000000000000000001"),
                },
            }
        },
    )
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
@pytest.mark.parametrize(
    "txid,delta",
    [
        (
            "0x037d4e123efdfcd382f99d961f048ff289af712c3b2f3c8bb142f19441a2f057",
            Decimal("10.000000000000000001"),
        ),  # positive tx
        (
            "44e25bc0ed840f9bf0e58d6227db15192d5b89e79ba4304da16b09703f68ceaf",
            Decimal("-10.000000000000000001"),
        ),  # negative tx
    ],
)
def test_update_wallet_balance_succeeds(
    authorized_api_client: APIClient, wallet: Wallet, txid: str, delta: Decimal
):
    initial_balance = wallet.balance

    # Create the wallet
    response = authorized_api_client.post(
        reverse("wallet-list"),
        {
            "data": {
                "type": "Wallet",
                "attributes": {
                    "label": wallet.label,
                    "balance": str(wallet.balance),
                    "user": wallet.user.pk,
                    "status": wallet.status,
                },
            }
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    wallet = Wallet.objects.get(pk=response.data.get("id"))

    response = authorized_api_client.post(
        reverse("tx-list"),
        {
            "data": {
                "type": "TX",
                "attributes": {
                    "wallet": wallet.id,
                    "txid": txid,
                    "amount": str(delta),
                },
            }
        },
    )
    assert response.status_code == status.HTTP_201_CREATED

    tx = TX.objects.get(pk=response.data.get("id"))
    assert tx.txid == txid
    assert tx.amount == delta

    # Refresh the wallet instance to get the updated balance and use the fixture wallet
    wallet = Wallet.objects.get(pk=wallet.id)
    assert wallet.balance == initial_balance + delta


@pytest.mark.django_db
@pytest.mark.parametrize(
    "txid,delta",
    [
        (
            "0x037d4e123efdfcd382f99d961f048ff289af712c3b2f3c8bb142f19441a2f057",
            Decimal("-10.00"),
        ),
        (
            "44e25bc0ed840f9bf0e58d6227db15192d5b89e79ba4304da16b09703f68ceaf",
            Decimal("-5.000000000000000001"),
        ),
    ],
)
def test_wallet_balance_cannot_go_below_zero(
    authorized_api_client: APIClient, wallet: Wallet, txid: str, delta: Decimal
):
    # Set initial balance to a small positive number
    wallet.balance = Decimal("5.00")
    response = authorized_api_client.post(
        reverse("wallet-list"),
        {
            "data": {
                "type": "Wallet",
                "attributes": {
                    "label": wallet.label,
                    "balance": str(wallet.balance),
                    "user": wallet.user.pk,
                    "status": wallet.status,
                },
            }
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    wallet = Wallet.objects.get(pk=response.data.get("id"))

    # Attempt to create a transaction that would make the balance negative
    response = authorized_api_client.post(
        reverse("tx-list"),
        {
            "data": {
                "type": "TX",
                "attributes": {
                    "wallet": wallet.id,
                    "txid": txid,
                    "amount": str(delta),
                },
            }
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "balance" in response.json()["errors"][0]["source"]["pointer"]

    # Verify that the wallet balance has not changed
    updated_wallet = Wallet.objects.get(pk=wallet.id)
    assert updated_wallet.balance == Decimal("5.00")


@pytest.mark.django_db
def test_wallet_list_pagination(authorized_api_client: APIClient, default_user: User):
    # Create 25 wallets for pagination testing
    for i in range(25):
        WalletFactory(user=default_user, label=f"Wallet {i}")

    # Test default pagination (page_size=10)
    response = authorized_api_client.get(reverse("wallet-list"))
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["data"]) == 10
    assert response.json()["meta"]["pagination"]["count"] == 25

    # Test second page
    response = authorized_api_client.get(reverse("wallet-list"), {"page[number]": 2})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["data"]) == 10

    # Test custom page size
    response = authorized_api_client.get(reverse("wallet-list"), {"page[size]": 5})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["data"]) == 5


@pytest.mark.django_db
def test_wallet_list_sorting(authorized_api_client: APIClient, default_user: User):
    # Create wallets with different labels for sorting
    WalletFactory(user=default_user, label="Wallet C")
    WalletFactory(user=default_user, label="Wallet A")
    WalletFactory(user=default_user, label="Wallet B")

    # Test sorting by label ascending
    response = authorized_api_client.get(reverse("wallet-list"), {"sort": "label"})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"][0]["attributes"]["label"] == "Wallet A"
    assert response.json()["data"][1]["attributes"]["label"] == "Wallet B"
    assert response.json()["data"][2]["attributes"]["label"] == "Wallet C"

    # Test sorting by label descending
    response = authorized_api_client.get(reverse("wallet-list"), {"sort": "-label"})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"][0]["attributes"]["label"] == "Wallet C"
    assert response.json()["data"][1]["attributes"]["label"] == "Wallet B"
    assert response.json()["data"][2]["attributes"]["label"] == "Wallet A"
