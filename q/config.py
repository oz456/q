"""
config.py - Production local configuration management (~/.q/config.json).

Handles loading, saving, and managing credentials and settings across multiple AI providers
(Google Gemini, OpenAI, Anthropic). Enforces POSIX 0600 file permissions for key security.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Tuple, Optional

CONFIG_DIR = Path.home() / ".q"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_MODELS = {
    "gemini": "gemini-2.5-flash",
    "openai": "gpt-4o-mini",
    "anthropic": "claude-3-5-haiku-20241022",
}

SUPPORTED_PROVIDERS = list(DEFAULT_MODELS.keys())


def get_default_config() -> Dict[str, Any]:
    """Returns a default configuration structure supporting all providers."""
    return {
        "active_provider": "gemini",
        "providers": {
            provider: {
                "api_key": "",
                "model": model,
            }
            for provider, model in DEFAULT_MODELS.items()
        },
    }


def load_config() -> Dict[str, Any]:
    """Loads config from ~/.q/config.json or returns default structure if missing/corrupt."""
    if not CONFIG_FILE.exists():
        return get_default_config()

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)

        default_config = get_default_config()
        if "active_provider" not in config:
            config["active_provider"] = default_config["active_provider"]
        if "providers" not in config:
            config["providers"] = default_config["providers"]
        else:
            for p, pdata in default_config["providers"].items():
                if p not in config["providers"]:
                    config["providers"][p] = pdata
                else:
                    config["providers"][p].setdefault("api_key", "")
                    config["providers"][p].setdefault("model", pdata["model"])

        return config
    except Exception:
        return get_default_config()


def save_config(config: Dict[str, Any]) -> None:
    """
    Saves configuration to ~/.q/config.json with POSIX 0600 file permissions.
    """
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

    try:
        os.chmod(CONFIG_FILE, 0o600)
    except Exception:
        pass


def get_active_provider(config: Dict[str, Any], override: Optional[str] = None) -> str:
    """Returns the validated active provider name."""
    provider = (override or config.get("active_provider", "gemini")).lower().strip()
    if provider not in SUPPORTED_PROVIDERS:
        return config.get("active_provider", "gemini")
    return provider


def get_provider_details(
    config: Dict[str, Any],
    provider_override: Optional[str] = None,
    model_override: Optional[str] = None,
) -> Tuple[str, str, str]:
    """Returns (provider_name, model_name, api_key) considering optional CLI overrides."""
    provider_name = get_active_provider(config, provider_override)
    provider_data = config.get("providers", {}).get(provider_name, {})

    model_name = model_override or provider_data.get("model") or DEFAULT_MODELS.get(provider_name, "")
    api_key = provider_data.get("api_key", "").strip()

    return provider_name, model_name, api_key


def has_api_key(config: Dict[str, Any], provider_name: Optional[str] = None) -> bool:
    """Checks if an API key is configured for the active or specified provider."""
    p_name = get_active_provider(config, provider_name)
    key = config.get("providers", {}).get(p_name, {}).get("api_key", "").strip()
    return bool(key)


def set_api_key(config: Dict[str, Any], provider_name: str, api_key: str) -> Dict[str, Any]:
    """Updates API key for specified provider and saves config."""
    p_name = provider_name.lower().strip()
    if p_name in SUPPORTED_PROVIDERS:
        config.setdefault("providers", {}).setdefault(p_name, {})["api_key"] = api_key.strip()
        save_config(config)
    return config


# Function alias for backwards compatibility
set_provider_key = set_api_key



def set_active_provider(config: Dict[str, Any], provider_name: str) -> Dict[str, Any]:
    """Sets active provider and saves config."""
    p_name = provider_name.lower().strip()
    if p_name in SUPPORTED_PROVIDERS:
        config["active_provider"] = p_name
        save_config(config)
    return config


def set_model(config: Dict[str, Any], provider_name: str, model_name: str) -> Dict[str, Any]:
    """Sets active model for specified provider and saves config."""
    p_name = provider_name.lower().strip()
    if p_name in SUPPORTED_PROVIDERS:
        config.setdefault("providers", {}).setdefault(p_name, {})["model"] = model_name.strip()
        save_config(config)
    return config


def reset_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Resets all provider keys and restores default configuration."""
    new_config = get_default_config()
    save_config(new_config)
    return new_config
