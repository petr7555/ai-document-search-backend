import os
import logging
from locust import HttpUser, task, between, events
from dotenv import load_dotenv


class TestUser(HttpUser):
    wait_time = between(0.5, 2)

    @events.quitting.add_listener
    def _(self, environment, **kw):
        if environment.stats.total.fail_ratio > 0.01:
            logging.error("Test failed due to failure ratio > 1%")
            environment.process_exit_code = 1
        elif environment.stats.total.avg_response_time > 15000:
            logging.error("Test failed due to average response time ratio > 200 ms")
            environment.process_exit_code = 1
        else:
            environment.process_exit_code = 0

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
