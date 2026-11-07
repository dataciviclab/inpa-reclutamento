"""Adapter minimale: API ``requests.Session`` su ``HttpClient``.

Gli script inPA usano una sessione solo per condividere header e POST JSON.
Qui il trasporto (retry, SSL fallback, proxy) è quello condiviso del Lab.
"""

from __future__ import annotations

from typing import Any

from lab_connectors.http import HttpClient


class Session:
    """Sostituto minimale di ``requests.Session`` basato su ``HttpClient``."""

    def __init__(self, *, timeout: int = 60) -> None:
        self._client = HttpClient(timeout=timeout, max_retries=1)
        self.headers: dict[str, str] = {}

    def post(
        self,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any = None,
        data: Any = None,
        timeout: int | None = None,
    ) -> Any:
        """POST e ritorna la ``requests.Response`` (o solleva RuntimeError)."""
        kwargs: dict[str, Any] = {"params": params, "json": json, "data": data, "retries": 1}
        if timeout is not None:
            kwargs["timeout"] = timeout
        if self.headers:
            kwargs["headers"] = dict(self.headers)
        result = self._client.post(url, **kwargs)
        if result.response is None:
            raise RuntimeError(f"POST {url} fallita: {result.err}")
        return result.response


__all__ = ["Session"]
