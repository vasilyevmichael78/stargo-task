"""Explicit HTTP adapters with no hidden retries or provider fallback."""

import json

import httpx

from .domain import AppError


class HTTPProvider:
    def __init__(self, settings, transport=None):
        self.settings, self.transport = settings, transport

    async def generate_structured(self, instructions, input, output_schema, timeout):
        url, headers, payload = self.request(instructions, input, output_schema)
        try:
            async with httpx.AsyncClient(
                timeout=timeout, transport=self.transport
            ) as client:
                response = await client.post(url, json=payload, headers=headers)
        except httpx.TimeoutException:
            raise AppError(
                "timeout",
                "The model request timed out. Retry or adjust the configured timeout.",
                True,
            ) from None
        except httpx.RequestError:
            raise AppError(
                "unavailable",
                "The configured model provider is unreachable. Check its setup and retry.",
                True,
            ) from None
        if response.status_code >= 400:
            if response.status_code in (401, 403):
                raise AppError(
                    "authentication",
                    "Provider authentication failed. Check your API key.",
                )
            if response.status_code == 429:
                error = AppError(
                    "rate_limit", "Provider rate limit reached. Wait and retry.", True
                )
                try:
                    error.retry_after = min(
                        5, max(0, float(response.headers.get("Retry-After", "1")))
                    )
                except ValueError:
                    error.retry_after = 1
                raise error
            if response.status_code == 404:
                raise AppError(
                    "configuration",
                    "Model or endpoint not found. Check the model name and provider setup.",
                )
            raise AppError(
                "unavailable",
                "The model provider rejected the request.",
                response.status_code >= 500,
            )
        try:
            return self.parse(response.json())
        except (ValueError, KeyError, IndexError, TypeError):
            raise AppError(
                "invalid_output", "The model returned an unreadable response.", True
            ) from None


class OllamaProvider(HTTPProvider):
    def request(self, instructions, input, schema):
        return (
            self.settings.ollama_base_url.rstrip("/") + "/api/chat",
            {},
            {
                "model": self.settings.model,
                "messages": [
                    {"role": "system", "content": instructions},
                    {"role": "user", "content": json.dumps(input)},
                ],
                "format": schema,
                "stream": False,
                "options": {"temperature": 0},
            },
        )

    def parse(self, body):
        return body["message"]["content"], {
            "input_tokens": body.get("prompt_eval_count"),
            "output_tokens": body.get("eval_count"),
        }


class GroqProvider(HTTPProvider):
    def request(self, instructions, input, schema):
        if not self.settings.groq_api_key:
            raise AppError("configuration", "Set GROQ_API_KEY in backend/.env.")
        return (
            "https://api.groq.com/openai/v1/chat/completions",
            {"Authorization": "Bearer " + self.settings.groq_api_key},
            {
                "model": self.settings.model,
                "messages": [
                    {
                        "role": "system",
                        "content": instructions
                        + "\nReturn JSON matching this schema: "
                        + json.dumps(schema),
                    },
                    {"role": "user", "content": json.dumps(input)},
                ],
                "temperature": 0,
                "response_format": {"type": "json_object"},
            },
        )

    def parse(self, body):
        return body["choices"][0]["message"]["content"], body.get("usage", {})


def create_provider(settings, transport=None):
    adapters = {"ollama": OllamaProvider, "groq": GroqProvider}
    if settings.llm_provider not in adapters:
        raise AppError("configuration", "LLM_PROVIDER must be ollama or groq.")
    return adapters[settings.llm_provider](settings, transport)
