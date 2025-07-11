from datetime import datetime, timezone
import os
import random

from locust import HttpUser, task, between


class BlockchainUser(HttpUser):
    wait_time = between(1, 4)

    def on_start(self):
        """
        On start, log in and get a token.
        """
        slug = datetime.now(tz=timezone.utc).strftime("%Y%m%d%H%M%S")
        self.token: str = self.client.post(
            "/api/v1/auth/token/",
            json={
                "username": os.environ["DJANGO_SUPERUSER_USER"],
                "password": os.environ["DJANGO_SUPERUSER_PASSWORD"],
            },
        ).json()["token"]

        self.user = self.client.post(
            "/api/v1/users/",
            headers={
                "Authorization": f"Token {self.token}",
                "Content-Type": "application/vnd.api+json",
            },
            json={
                "data": {
                    "type": "User",
                    "attributes": {
                        "username": f"testuser_{slug}",
                        "password": "testpassword",
                        "first_name": "lo",
                        "last_name": "cust",
                        "email": "testuser_{slug}@lo.cust",
                    },
                }
            },
        ).json()["data"]
        print(f"testuser_{slug}: ", self.user["id"])

    @task
    def create_wallet(self):
        label = f"Wallet {random.randint(0, 1000000)}"
        balance = str(random.uniform(1, 1000))

        self.client.post(
            "/api/v1/wallets/",
            headers={
                "Authorization": f"Token {self.token}",
                "Content-Type": "application/vnd.api+json",
            },
            json={
                "data": {
                    "type": "Wallet",
                    "attributes": {
                        "label": label,
                        "balance": balance,
                        "user": self.user["id"],
                        "status": "A",
                    },
                }
            },
            name="/api/v1/wallets/ [POST] - Create Wallet",
        )

    @task
    def create_transaction(self):
        # First, create a wallet to associate the transaction with
        label = f"Wallet {random.randint(0, 1000000)}"
        balance = str(random.uniform(1, 1000))

        wallet_response = self.client.post(
            "/api/v1/wallets/",
            headers={
                "Authorization": f"Token {self.token}",
                "Content-Type": "application/vnd.api+json",
            },
            json={
                "data": {
                    "type": "Wallet",
                    "attributes": {
                        "label": label,
                        "balance": balance,
                        "user": self.user["id"],
                        "status": "A",
                    },
                }
            },
            name="/api/v1/wallets/ [POST] - Create Wallet",
        )
        if wallet_response.status_code == 201:
            wallet_id = wallet_response.json()["data"]["id"]
            txid = f"0x{random.randbytes(32).hex()}"
            amount = str(random.uniform(0, 100))

            self.client.post(
                "/api/v1/transactions/",
                headers={
                    "Authorization": f"Token {self.token}",
                    "Content-Type": "application/vnd.api+json",
                },
                json={
                    "data": {
                        "type": "TX",
                        "attributes": {
                            "wallet": wallet_id,
                            "txid": txid,
                            "amount": amount,
                        },
                    }
                },
                name="/api/v1/transactions/ [POST] - Create Transaction",
            )
