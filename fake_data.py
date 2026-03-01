from faker import Faker
import httpx

def get_auth_token():
    response = httpx.post(
        "http://localhost:8000/api/auth/token",
        data={"username": "user1", "password": "test1234"},
    )
    return response.json()["access_token"]

fake = Faker()

for i in range(10):
    httpx.post(
        "http://localhost:8000/api/shorten", 
        json={"url": fake.url()}, 
        headers={"Authorization": f"Bearer {get_auth_token()}"})
        