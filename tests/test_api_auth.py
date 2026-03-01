class TestRegister:
    REGISTER_URL = "/api/auth/register"

    def test_register_success(self, client):
        response = client.post(self.REGISTER_URL, json={
            "username": "newuser",
            "password": "securepassword123",
        })
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["username"] == "newuser"
        assert "password" not in data

    def test_register_duplicate_username(self, client):
        payload = {"username": "duplicate", "password": "securepassword123"}
        client.post(self.REGISTER_URL, json=payload)

        response = client.post(self.REGISTER_URL, json=payload)
        assert response.status_code == 409

    def test_register_short_password(self, client):
        response = client.post(self.REGISTER_URL, json={
            "username": "shortpwd",
            "password": "short",
        })
        assert response.status_code == 422


class TestToken:
    REGISTER_URL = "/api/auth/register"
    TOKEN_URL = "/api/auth/token"

    def _create_user(self, client, username="tokenuser", password="securepassword123"):
        client.post(self.REGISTER_URL, json={
            "username": username,
            "password": password,
        })

    def test_token_correct_credentials(self, client):
        self._create_user(client)

        response = client.post(self.TOKEN_URL, data={
            "username": "tokenuser",
            "password": "securepassword123",
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_token_wrong_password(self, client):
        self._create_user(client)

        response = client.post(self.TOKEN_URL, data={
            "username": "tokenuser",
            "password": "wrongpassword123",
        })
        assert response.status_code == 401

    def test_token_nonexistent_user(self, client):
        response = client.post(self.TOKEN_URL, data={
            "username": "ghost",
            "password": "doesnotmatter1",
        })
        assert response.status_code == 401
