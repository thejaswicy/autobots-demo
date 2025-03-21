import jwt
import time
import requests
import os
import json

# GitHub App credentials
APP_ID = os.getenv("GITHUB_APP_ID")
PRIVATE_KEY = os.getenv("GITHUB_PRIVATE_KEY")
GITHUB_API_URL = os.getenv("GITHUB_API_URL", "https://api.github.com")

# Proxy settings (for self-hosted runners)
PROXY_URL = os.getenv("HTTPS_PROXY") or os.getenv("HTTP_PROXY")
NO_PROXY = os.getenv("NO_PROXY", "").split(",")

def get_proxies():
    """Return proxy settings if configured."""
    if PROXY_URL:
        return {"https": PROXY_URL, "http": PROXY_URL}
    return {}

def generate_jwt():
    """Generate a JWT using the GitHub App's private key."""
    private_key = PRIVATE_KEY.replace("\\n", "\n")  # Convert secret to valid format

    payload = {
        "iat": int(time.time()),  # Issued at time
        "exp": int(time.time()) + (10 * 60),  # Expires in 10 minutes
        "iss": APP_ID  # GitHub App ID
    }

    return jwt.encode(payload, private_key, algorithm="RS256")

def get_installation_id(jwt_token):
    """Fetch the GitHub App installation ID dynamically."""
    url = f"{GITHUB_API_URL}/app/installations"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github.v3+json"
    }

    response = requests.get(url, headers=headers, proxies=get_proxies())

    if response.status_code == 200:
        installations = response.json()
        if installations:
            return installations[0]["id"]  # Assuming only one installation
        else:
            raise Exception("No installations found for the GitHub App.")
    else:
        raise Exception(f"Failed to get installation ID: {response.text}")

def get_access_token(installation_id, jwt_token):
    """Exchange the JWT for an installation access token."""
    url = f"{GITHUB_API_URL}/app/installations/{installation_id}/access_tokens"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github.v3+json"
    }

    response = requests.post(url, headers=headers, proxies=get_proxies())

    if response.status_code == 201:
        return response.json()["token"]
    else:
        raise Exception(f"Failed to get access token: {response.text}")

if __name__ == "__main__":
    try:
        jwt_token = generate_jwt()
        installation_id = get_installation_id(jwt_token)
        access_token = get_access_token(installation_id, jwt_token)

        print(f"::add-mask::{access_token}")  # Mask the token in logs
        print(f"::set-output name=access_token::{access_token}")  # Set output for GitHub Actions

    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1)
