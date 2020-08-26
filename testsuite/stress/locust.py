from pathlib import Path

from locust import HttpUser, between, task


FILEPATH = Path("testsuite") / "test.zip"


class StudentUser(HttpUser):
    wait_time = between(5, 15)

    def on_start(self):
        self.username = "admin"
        self.password = "admin"

        response = self.client.get("/")
        csrftoken = response.cookies["csrftoken"]
        login_info = {
            "username": self.username,
            "password": self.password,
        }

        self.client.post("/", login_info, headers={"X-CSRFToken": csrftoken})

    @task
    def homepage(self):
        self.client.get("/homepage")

    @task
    def submission(self):
        self.client.get("/submission")

    @task
    def mysubmissions(self):
        self.client.get(f"/mysubmissions/{self.username}")

    @task
    def upload_homework(self):
        response = self.client.get("/assignment/1/2/upload/")
        csrftoken = response.cookies["csrftoken"]

        with open(FILEPATH, "rb") as f_in:
            response = self.client.post(
                "/assignment/1/2/upload/",
                files={"file": f_in},
                headers={"X-CSRFToken": csrftoken},
                data={"id": "42"},
                timeout=5,
            )

    def on_stop(self):
        response = self.client.get("/assignment/1/2/upload/")
        csrftoken = response.cookies["csrftoken"]

        self.client.post("/logout/", headers={"X-CSRFToken": csrftoken})
