import requests
from datetime import datetime
from utils import load_profiles, get_profile, save_profiles, get_default_profile_name, get_by_path
from token_utils import get_token_expiry, is_token_valid

def login(profile: dict):
    url = profile["url"]
    payload = profile.get("payload")
    response_mapping = profile.get("response_mapping")

    if not url:
        raise ValueError("Profile is missing 'url'")
    if payload is None:
        raise ValueError("Profile is missing 'payload'")
    if response_mapping is None:
        raise ValueError("Profile is missing 'response_mapping'")
    

    print(f"Sending request to {url} with login details: {payload["username"]}")
    response = requests.post(url, json=payload)


    try:
        data = response.json()
    except requests.exceptions.JSONDecodeError:
        raise Exception(
            f"The API returned a non-JSON response.\n"
            f"Status Code: {response.status_code}\n"
            f"Content-Type: {response.headers.get('Content-Type')}\n"
            f"Response: {response.text[:500]}"
        )

    success_path = response_mapping.get("success_path")
    error_path = response_mapping.get("error_path")
    token_path = response_mapping.get("token_path")

    success = get_by_path(data, success_path) if success_path else None
    errors = get_by_path(data, error_path) if error_path else None
    token = get_by_path(data, token_path) if token_path else None

    if response.status_code >= 400:
        raise Exception(f"Login failed ({response.status_code}): {errors or data}")
    
    if success is False:
        raise Exception(f"Login failed: {errors or data}")

    if not isinstance(token, str) or not token.strip():
        raise Exception(
            f"Login succeeded but no access token found.\n"
            f"Response: {data}"
        )

    print("Login successful")
    return token


def run_login(profile_name: str|None = None, fresh: bool = False):
    profile = get_profile(profile_name)
    name = profile_name or get_default_profile_name()

    if name is None:
        raise ValueError("No profile name provided and no default profile configured.")

    token, expiry = get_cached_token(profile)

    if not fresh and token and (expiry is None or is_token_valid(expiry)):
        print("Using cached token")
        return token

    if fresh:
        print("Forcing fresh login...")

    print("Logging in...")

    token = login(profile)

    expiry = get_token_expiry(token)

    cache_token(name, token, expiry)

    # Set the default profile if one has not been configured
    data = load_profiles()

    if not data.get("default"):
        data["default"] = name
        save_profiles(data)
        print(f"Default profile set to: {name}")

    return token

def cache_token(profile_name: str, token: str, expiry: datetime|None):
    data = load_profiles()

    data["profiles"][profile_name]["cache"] = {
        "access_token": token,
        "expires_at": expiry.isoformat() if expiry else None
    }
    save_profiles(data)

def get_cached_token(profile: dict):
    cache = profile.get("cache")

    if not cache:
        return None, None

    token = cache.get("access_token")
    expiry_str = cache.get("expires_at")

    expiry = datetime.fromisoformat(expiry_str) if expiry_str else None

    return token, expiry
