
import json
from typing import Any
from platformdirs import user_config_dir
from pathlib import Path

CONFIG_DIR = Path(user_config_dir(appname="AuthHelper", appauthor=False))
PROFILES_FILE = CONFIG_DIR / "profiles.json"

# The old configuration location, relative to this project
LEGACY_PROFILES_FILE = Path(__file__).parent / "profiles.json"


def create_default_config() -> dict:
    return {
        "default": None,
        "profiles": {}
    }


def migrate_config():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    # If the new configuration already exists, don't overwrite it
    if PROFILES_FILE.exists():
        return

    # If an old configuration exists, migrate it
    if LEGACY_PROFILES_FILE.exists():
        with open(LEGACY_PROFILES_FILE, "r") as f:
            data = json.load(f)

        save_profiles(data)

        print("Existing configuration migrated successfully.")
        return

    # No existing configuration: create a fresh one
    save_profiles(create_default_config())


def load_profiles() -> dict:
    migrate_config()

    with open(PROFILES_FILE, "r") as f:
        return json.load(f)


def get_profile(name: str | None = None) -> dict:
    data = load_profiles()

    if not name:
        name = data["default"]

    if not name:
        raise ValueError("No profile specified and no default profile is configured. to set a default profile, use the 'use' command. or login with a specific profile using 'auth login <profile_name>'.")

    if name not in data["profiles"]:
        raise ValueError(f"Profile '{name}' does not exist.")
    
    return data["profiles"][name]


def save_profiles(data: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    with open(PROFILES_FILE, "w") as f:
        json.dump(data, f, indent="\t")


def get_default_profile_name() -> str | None:
    data = load_profiles()
    return data.get("default")


def get_by_path(data: dict[str, Any], path: str) -> Any:
    keys = path.split(".")
    current: Any = data

    for key in keys:
        if not isinstance(current, dict):
            return None

        current = current.get(key)

    return current