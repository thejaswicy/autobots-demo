"""Python script to generate access_token for GitHub Actions using a GitHub App."""
import jwt
import time
import requests
import os

# GitHub App credentials
APP_ID = os.getenv("GITHUB_APP_ID")
PRIVATE_KEY_PATH = os.getenv("GITHUB_PRIVATE_KEY_PATH")
GITHUB_API_URL = os.getenv("GITHUB_API_URL", "https://api.github.com")

# Proxy settings (for self-hosted runners)
PROXY_URL = os.getenv("HTTPS_PROXY") or os.getenv("HTTP_PROXY")
NO_PROXY = os.getenv("NO_PROXY", "").split(",")

session = requests.Session()  # Reuse session for efficiency

def get_proxies():
    """Apply proxy settings if needed."""
    if PROXY_URL:
        return {"https": PROXY_URL, "http": PROXY_URL}
    return {}

def generate_jwt():
    """Generate a JWT using the GitHub App's private key."""
    with open(PRIVATE_KEY_PATH, "rb") as key_file:
        private_key = key_file.read()

    payload = {
        "iat": int(time.time()),  # Issued at time
        "exp": int(time.time()) + (10 * 60),  # Expires in 10 minutes
        "iss": APP_ID  # GitHub App ID
    }

    return jwt.encode(payload, private_key, algorithm="RS256")

def get_installation_id(jwt_token):
    """Retrieve the installation ID dynamically from GitHub API."""
    url = f"{GITHUB_API_URL}/app/installations"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github.v3+json"
    }

    response = session.get(url, headers=headers, proxies=get_proxies())

    if response.status_code == 200:
        installations = response.json()
        if not installations:
            raise Exception("No installations found for this GitHub App.")
        return installations[0]["id"]  # Return the first installation ID
    else:
        raise Exception(f"Failed to get installation ID: {response.text}")

def get_access_token(jwt_token, installation_id):
    """Exchange the JWT for an installation access token."""
    url = f"{GITHUB_API_URL}/app/installations/{installation_id}/access_tokens"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github.v3+json"
    }

    response = session.post(url, headers=headers, proxies=get_proxies())

    if response.status_code == 201:
        return response.json()["token"]
    else:
        raise Exception(f"Failed to get access token: {response.text}")

def revoke_token(access_token):
    """Revoke the access token to avoid security risks."""
    url = f"{GITHUB_API_URL}/installation/token"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github.v3+json"
    }

    response = session.delete(url, headers=headers, proxies=get_proxies())

    if response.status_code == 204:
        print("✅ Token successfully revoked.")
    else:
        print(f"⚠️ Failed to revoke token: {response.text}")

if __name__ == "__main__":
    try:
        jwt_token = generate_jwt()
        installation_id = get_installation_id(jwt_token)
        access_token = get_access_token(jwt_token, installation_id)

        print(f"::add-mask::{access_token}")  # Mask token in GitHub Actions logs
        print(f"::set-output name=access_token::{access_token}")  # Output for Actions

        # Ensure token is revoked at the end of the job
        revoke_token(access_token)

    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1)
