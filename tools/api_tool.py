import requests
from typing import Optional

class APITool:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.token: Optional[str] = None

    def login(self, email: str, password: str) -> bool:
        """Authenticate and store the JWT token."""
        url = f"{self.base_url}/auth/signin"
        payload = {
            "email": email,
            "password": password
        }
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            self.token = data.get("access_token")
            return True if self.token else False
        except requests.exceptions.RequestException as e:
            print(f"Login failed: {e}")
            return False

    def call_api(self, endpoint: str, method: str = "GET", data: Optional[dict] = None):
        """Call an API endpoint with the stored token."""
        if not self.token:
            raise ValueError("You must log in to obtain a token before making API calls.")

        url = f"{self.base_url}{endpoint}"
        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            if method == "GET":
                response = requests.get(url, headers=headers)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API call failed: {e}")
            return {"error": str(e)}
