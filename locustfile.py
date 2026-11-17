import time
from locust import HttpUser, task, between
from app.utils.security import create_access_token

class ShopSenseLoadTestUser(HttpUser):
    wait_time = between(1, 2)

    def on_start(self):
        # Generate valid Admin JWT token for benchmarking authenticated endpoints
        self.token = create_access_token(data={"sub": "admin@shopsense.com", "role": "ADMIN"})
        self.headers = {"Authorization": f"Bearer {self.token}"}

    @task(3)
    def test_revenue_analytics(self):
        self.client.get("/analytics/revenue", headers=self.headers, name="GET /analytics/revenue")

    @task(3)
    def test_vendor_performance(self):
        self.client.get("/analytics/vendor-performance", headers=self.headers, name="GET /analytics/vendor-performance")

    @task(2)
    def test_customer_analytics(self):
        self.client.get("/analytics/customers", headers=self.headers, name="GET /analytics/customers")

    @task(1)
    def test_forecast_overview(self):
        self.client.get("/analytics/forecast", headers=self.headers, name="GET /analytics/forecast")

    @task(2)
    def test_recommendation_evaluation(self):
        self.client.get("/api/recommendations/evaluation", headers=self.headers, name="GET /api/recommendations/evaluation")
