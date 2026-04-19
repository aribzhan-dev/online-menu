from locust import HttpUser, task

class MyUser(HttpUser):

    @task
    def products(self):
        self.client.get("/api/menu/1/products")

    @task
    def search(self):
        self.client.get("/api/menu/1/search?q=Пеперони")