from locust import HttpUser, task, between

class TestUser(HttpUser):
    wait_time = between(1,5)
    test_username = "test"
    test_password = "pass"

    @task
    def authenticate(self):
        self.client.get("/health")

    @task
    def authenticate(self):
        response = self.client.post(
        "/auth/token", data={"username": self.test_username, "password": self.test_password}
    )
        
    @task
    def get_conversation(self):
        response = self.client.post("/auth/token", data={"username": self.test_username, "password": self.test_password})
        token = response.json()["access_token"]
        response = self.client.get("/conversation", headers={"Authorization": f"Bearer {token}"})

    @task
    def ask_question(self):
        response = self.client.post("/auth/token", data={"username": self.test_username, "password": self.test_password})
        token = response.json()["access_token"]

        response = self.client.post(
        "/chatbot/",
        headers={"Authorization": f"Bearer {token}"},
        json={"question": "What is the Loan to value ratio?"},
    )