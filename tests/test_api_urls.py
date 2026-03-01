class TestShortenUrl:
    SHORTEN_URL = "/api/shorten"

    def _auth_header(self, token):
        return {"Authorization": f"Bearer {token}"}

    def test_shorten_with_valid_token(self, client, auth_token):
        response = client.post(
            self.SHORTEN_URL,
            json={"url": "https://example.com"},
            headers=self._auth_header(auth_token),
        )
        assert response.status_code == 201
        data = response.json()
        assert "short_url" in data
        assert data["short_url"].startswith("http://testserver/api/")

    def test_shorten_without_token(self, client):
        response = client.post(
            self.SHORTEN_URL,
            json={"url": "https://example.com"},
        )
        assert response.status_code == 401

    def test_shorten_invalid_url(self, client, auth_token):
        response = client.post(
            self.SHORTEN_URL,
            json={"url": "not-a-url"},
            headers=self._auth_header(auth_token),
        )
        assert response.status_code == 422

    def test_shorten_same_url_returns_same_code(self, client, auth_token):
        headers = self._auth_header(auth_token)
        url_payload = {"url": "https://example.com/same"}

        first = client.post(self.SHORTEN_URL, json=url_payload, headers=headers)
        second = client.post(self.SHORTEN_URL, json=url_payload, headers=headers)

        assert first.status_code == 201
        assert second.status_code == 201
        assert first.json()["short_url"] == second.json()["short_url"]


class TestRedirect:
    SHORTEN_URL = "/api/shorten"

    def _auth_header(self, token):
        return {"Authorization": f"Bearer {token}"}

    def _create_short_url(self, client, token, url="https://example.com/redirect"):
        response = client.post(
            self.SHORTEN_URL,
            json={"url": url},
            headers=self._auth_header(token),
        )
        short_url = response.json()["short_url"]
        short_code = short_url.rsplit("/", 1)[-1]
        return short_code

    def test_redirect_existing_code(self, client, auth_token):
        short_code = self._create_short_url(client, auth_token)

        response = client.get(f"/api/{short_code}")
        assert response.status_code == 200

    def test_redirect_nonexistent_code(self, client):
        response = client.get("/api/nonexistent123")
        assert response.status_code == 404


class TestGetAll:
    SHORTEN_URL = "/api/shorten"
    GET_ALL_URL = "/api/get-all"

    def _auth_header(self, token):
        return {"Authorization": f"Bearer {token}"}

    def test_get_all_with_token(self, client, auth_token):
        headers = self._auth_header(auth_token)

        client.post(self.SHORTEN_URL, json={"url": "https://a.com"}, headers=headers)
        client.post(self.SHORTEN_URL, json={"url": "https://b.com"}, headers=headers)

        response = client.get(self.GET_ALL_URL, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2

    def test_get_all_without_token(self, client):
        response = client.get(self.GET_ALL_URL)
        assert response.status_code == 401
