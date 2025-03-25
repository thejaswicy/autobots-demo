import jwt
import time
import requests
import os

APP_ID = os.getenv("GITHUB_APP_ID")
PRIVATE_KEY = os.getenv("GITHUB_PRIVATE_KEY")
GITHUB_API_URL = os.getenv("GITHUB_API_URL", "https://api.github.com")

def generate_jwt():
    private_key = PRIVATE_KEY.replace("\\n", "\n")
    payload = {
        "iat": int(time.time()),
        "exp": int(time.time()) + (10 * 60),
        "iss": APP_ID
    }
    return jwt.encode(payload, private_key, algorithm="RS256")

def get_installation_id(jwt_token):
    url = f"{GITHUB_API_URL}/app/installations"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()[0]["id"]

def get_access_token(installation_id, jwt_token):
    url = f"{GITHUB_API_URL}/app/installations/{installation_id}/access_tokens"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.post(url, headers=headers)
    response.raise_for_status()
    return response.json()["token"]

if __name__ == "__main__":
    try:
        jwt_token = generate_jwt()
        installation_id = get_installation_id(jwt_token)
        access_token = get_access_token(installation_id, jwt_token)

        # Mask the token in logs
        # print(f"::add-mask::{access_token}")

        # ✅ Correct way to pass output
        with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
            print(f"access_token={access_token}", file=f)

    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1)
