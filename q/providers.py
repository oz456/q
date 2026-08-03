"""
providers.py - Multi-provider AI streaming wrappers (Google Gemini, OpenAI, Anthropic).

Abstracts all three major AI providers behind a unified streaming interface using standard
HTTP Server-Sent Events (SSE). Lightweight, fast, transparent, and free of heavy SDK conflicts.
"""

import json
from typing import List, Dict, Generator
import requests


class BaseProvider:
    """Base class for AI streaming providers."""

    def stream(self, messages: List[Dict[str, str]], model: str, api_key: str) -> Generator[str, None, None]:
        """Streams response token chunks live as they arrive."""
        raise NotImplementedError("Subclasses must implement stream().")


class GeminiProvider(BaseProvider):
    """Google Gemini API streaming client."""

    def stream(self, messages: List[Dict[str, str]], model: str, api_key: str) -> Generator[str, None, None]:
        if not api_key:
            raise ValueError("Google Gemini API key is missing. Run 'q --setup' or '/key' to configure it.")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:streamGenerateContent?alt=sse&key={api_key}"

        # Gemini API schema expects role 'model' for past assistant turns
        contents = []
        for msg in messages:
            role = "model" if msg["role"] == "assistant" else "user"
            contents.append({
                "role": role,
                "parts": [{"text": msg["content"]}]
            })

        payload = {"contents": contents}

        try:
            response = requests.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                stream=True,
                timeout=30
            )
        except requests.RequestException as e:
            raise RuntimeError(f"Network error connecting to Google Gemini API: {e}")

        if response.status_code != 200:
            err_msg = f"Gemini API Error (HTTP {response.status_code})"
            try:
                err_data = response.json()
                if "error" in err_data and "message" in err_data["error"]:
                    err_msg = err_data["error"]["message"]
            except Exception:
                pass
            raise RuntimeError(err_msg)

        for line in response.iter_lines():
            if not line:
                continue
            line_str = line.decode("utf-8")
            if line_str.startswith("data: "):
                data_json = line_str[6:].strip()
                try:
                    data = json.loads(data_json)
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        for part in parts:
                            text = part.get("text", "")
                            if text:
                                yield text
                except json.JSONDecodeError:
                    continue


class OpenAIProvider(BaseProvider):
    """OpenAI API streaming client."""

    def stream(self, messages: List[Dict[str, str]], model: str, api_key: str) -> Generator[str, None, None]:
        if not api_key:
            raise ValueError("OpenAI API key is missing. Run 'q --setup' or '/key' to configure it.")

        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": messages,
            "stream": True,
        }

        try:
            response = requests.post(url, json=payload, headers=headers, stream=True, timeout=30)
        except requests.RequestException as e:
            raise RuntimeError(f"Network error connecting to OpenAI API: {e}")

        if response.status_code != 200:
            err_msg = f"OpenAI API Error (HTTP {response.status_code})"
            try:
                err_data = response.json()
                if "error" in err_data and "message" in err_data["error"]:
                    err_msg = err_data["error"]["message"]
            except Exception:
                pass
            raise RuntimeError(err_msg)

        for line in response.iter_lines():
            if not line:
                continue
            line_str = line.decode("utf-8")
            if line_str.startswith("data: "):
                data_str = line_str[6:].strip()
                if data_str == "[DONE]":
                    break
                try:
                    data = json.loads(data_str)
                    choices = data.get("choices", [])
                    if choices:
                        delta = choices[0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            yield content
                except json.JSONDecodeError:
                    continue


class AnthropicProvider(BaseProvider):
    """Anthropic (Claude) API streaming client."""

    def stream(self, messages: List[Dict[str, str]], model: str, api_key: str) -> Generator[str, None, None]:
        if not api_key:
            raise ValueError("Anthropic API key is missing. Run 'q --setup' or '/key' to configure it.")

        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

        system_prompt = ""
        anthropic_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_prompt = msg["content"]
            else:
                anthropic_messages.append({"role": msg["role"], "content": msg["content"]})

        payload = {
            "model": model,
            "max_tokens": 2048,
            "messages": anthropic_messages,
            "stream": True,
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            response = requests.post(url, json=payload, headers=headers, stream=True, timeout=30)
        except requests.RequestException as e:
            raise RuntimeError(f"Network error connecting to Anthropic API: {e}")

        if response.status_code != 200:
            err_msg = f"Anthropic API Error (HTTP {response.status_code})"
            try:
                err_data = response.json()
                if "error" in err_data and "message" in err_data["error"]:
                    err_msg = err_data["error"]["message"]
            except Exception:
                pass
            raise RuntimeError(err_msg)

        for line in response.iter_lines():
            if not line:
                continue
            line_str = line.decode("utf-8")
            if line_str.startswith("data: "):
                data_str = line_str[6:].strip()
                try:
                    data = json.loads(data_str)
                    if data.get("type") == "content_block_delta":
                        delta = data.get("delta", {})
                        text = delta.get("text", "")
                        if text:
                            yield text
                except json.JSONDecodeError:
                    continue


def get_provider_instance(provider_name: str) -> BaseProvider:
    """Factory function returning the provider implementation for a provider key."""
    p_name = provider_name.lower().strip()
    if p_name == "gemini":
        return GeminiProvider()
    elif p_name == "openai":
        return OpenAIProvider()
    elif p_name == "anthropic":
        return AnthropicProvider()
    else:
        raise ValueError(f"Unsupported provider '{provider_name}'. Supported: gemini, openai, anthropic.")
