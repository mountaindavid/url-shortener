class TestHealth:

    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_status_healthy(self, client):
        response = client.get("/health")
        assert response.json() == {"status": "healthy"}
