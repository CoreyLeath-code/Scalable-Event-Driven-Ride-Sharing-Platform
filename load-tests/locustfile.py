from locust import HttpUser, task, between


class RideUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def request_ride(self):
        self.client.post(
            "/request-ride",
            json={
                "rider_id": "123",
                "pickup_lat": 40.7,
                "pickup_lng": -74.0,
                "destination_lat": 40.8,
                "destination_lng": -73.9,
            },
        )
