# commands.py

from datetime import datetime, timezone
from getpass import getpass
from urllib.parse import urlparse
from utils import load_profiles, save_profiles
from token_utils import is_token_valid

def set_default_profile(profile_name):
    data = load_profiles()

    if profile_name not in data["profiles"]:
        raise Exception(f"Profile '{profile_name}' not found")

    data["default"] = profile_name
    save_profiles(data)

    print(f"Now using profile: {profile_name}")


def list_profiles():
    data = load_profiles()
    default = data.get("default")

    print("\nProfiles:\n")

    for name in data["profiles"]:
        marker = " (active)" if name == default else ""
        print(f" - {name}{marker}")


def show_current():
    data = load_profiles()
    print(f"Current profile: {data.get('default')}")

def status():
    data = load_profiles()
    profile_name = data.get("default")

    if not profile_name:
        print("No default profile configured.")
        return

    profile = data["profiles"].get(profile_name)

    if not profile:
        print(f"Profile '{profile_name}' not found.")
        return

    cache = profile.get("cache", {})
    token = cache.get("access_token")
    expires_at = cache.get("expires_at")

    print("\nAuth Helper Status")
    print("------------------")
    print(f"Profile: {profile_name}")

    if not token:
        print("Authentication: Not authenticated")
        return

    if not expires_at:
        print("Authentication: Token cached")
        print("Token Status: Unknown (no expiry information)")
        return

    expiry = datetime.fromisoformat(expires_at)

    if is_token_valid(expiry):
        remaining = expiry - datetime.now(timezone.utc)

        total_seconds = int(remaining.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        print("Authentication: Authenticated")
        print("Token Status: Valid")
        print(f"Expires At: {expiry.strftime('%d %b %Y, %H:%M:%S UTC')}")
        print(f"Time Remaining: {hours}h {minutes}m {seconds}s")

    else:
        print("Authentication: Not authenticated")
        print("Token Status: Expired")
        print(f"Expired At: {expiry.strftime('%d %b %Y, %H:%M:%S UTC')}")


def add_profile():
    data = load_profiles()

    print("\nCreate a new API profile")
    print("------------------------")

    name = input("Profile name: ").strip()

    if not name:
        print("Profile name cannot be empty.")
        return

    if name in data["profiles"]:
        print(f"Profile '{name}' already exists.")
        return

    url = input("Login URL: ").strip()

    if not url:
        print("Login URL cannot be empty.")
        return

    parsed_url = urlparse(url)

    if parsed_url.scheme not in ("http", "https") or not parsed_url.netloc:
        print("Invalid URL. Please enter a valid HTTP or HTTPS URL.")
        return

    print("\nConfigure login payload")
    print("---------------------")
    print("Enter the fields required by your API.")
    print("Type 'done' when finished.\n")

    payload = {}

    sensitive_fields = {
        "password",
        "passwd",
        "secret",
        "client_secret",
        "api_key",
        "apikey"
    }

    while True:
        key = input("\nField name (or 'done'): ").strip()

        if key.lower() == "done":
            break

        if not key:
            continue

        if key in payload:
            print(f"Field '{key}' already exists.")
            continue

        if key.lower() in sensitive_fields:
            value = getpass(f"enter '{key}' value: ")
        else:
            value = input(f"enter '{key}' value: ")

        payload[key] = value

    print("\nResponse mapping")
    print("--------------")
    print("Enter the JSON paths used by your API response. That is, the keys in the JSON response that contain the access token, error messages, and success indicators.\n")
    print("Press Enter to skip optional fields.\n")

    token_path = input('Token path (e.g. data.accessToken in "{\"data\":{\"accessToken\": \"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...\"}}): ').strip()

    if not token_path:
        print("Token path is required.")
        return

    error_path = input('\nError path (optional, e.g. errors in "{\"errors\": [...]}"): ').strip()

    success_path = input('\nSuccess path (optional, e.g. success in "{\"success\": true}"): ').strip()

    profile = {
        "payload": payload,
        "url": url,
        "response_mapping": {
            "token_path": token_path
        },
        "cache": {
            "access_token": "",
            "expires_at": ""
        }
    }

    if error_path:
        profile["response_mapping"]["error_path"] = error_path

    if success_path:
        profile["response_mapping"]["success_path"] = success_path

    data["profiles"][name] = profile

    save_profiles(data)

    print(f"\nProfile '{name}' created successfully.")

def remove_profile(profile_name: str | None = None):
    data = load_profiles()

    profiles = data.get("profiles", {})
    default_profile = data.get("default")

    if not profiles:
        print("No profiles available.")
        return

    # If no profile name was provided, display available profiles
    if not profile_name:
        print("\nAvailable profiles:\n")

        for name in profiles:
            marker = " (default)" if name == default_profile else ""
            print(f" - {name}{marker}")

        print("\nUsage: auth remove-profile <profile_name>")
        return

    # Ensure the profile exists
    if profile_name not in profiles:
        print(f"Profile '{profile_name}' not found.")
        return

    # Prevent accidental deletion of the default profile
    if profile_name == default_profile:
        print(
            f"Cannot remove '{profile_name}' because it is your default profile.\n"
            "Switch to another profile first using the 'use' command."
        )
        return

    # Confirm deletion
    confirmation = input(
        f"Are you sure you want to remove profile '{profile_name}'? (y/N): "
    ).strip().lower()

    if confirmation != "y":
        print("Profile removal cancelled.")
        return

    # Remove the profile and its cached token
    del profiles[profile_name]

    save_profiles(data)

    print(f"Profile '{profile_name}' removed successfully.")