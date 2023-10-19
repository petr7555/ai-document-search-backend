import os
from locust import HttpUser, task, between
from dotenv import load_dotenv


class TestUser(HttpUser):
    wait_time = between(0.5, 2)

    def credentials(self):
        load_dotenv()
        test_username = os.getenv("AUTH_USERNAME")
        test_password = os.getenv("AUTH_PASSWORD")
        return test_username, test_password

    @task
    def health(self):
        self.client.get("/health")

    @task
    def authenticate(self):
        test_username, test_password = self.credentials()
        self.client.post("/auth/token", data={"username": test_username, "password": test_password})

    @task
    def get_conversation(self):
        test_username, test_password = self.credentials()
        response = self.client.post(
            "/auth/token", data={"username": test_username, "password": test_password}
        )
        token = response.json()["access_token"]
        response = self.client.get("/conversation", headers={"Authorization": f"Bearer {token}"})

    @task
    def ask_question(self):
        test_username, test_password = self.credentials()
        response = self.client.post(
            "/auth/token", data={"username": test_username, "password": test_password}
        )
        token = response.json()["access_token"]

        response = self.client.post(
            "/chatbot",
            headers={"Authorization": f"Bearer {token}"},
            json={"question": "What is the Loan to value ratio?"},
        )
