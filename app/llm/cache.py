"""Optional caching layer – currently a simple in‑memory dict.

If you want to use Redis, replace the implementation below with a
Redis client (e.g. `aioredis`).  The rest of the code only imports
`CACHE_ENABLED` and calls `cache_get`/`cache_set`.
"""

from __future__ import annotations

import json
from typing import Any, Dict

# In‑memory cache for demo purposes
_CACHE: Dict[str, Any] = {}

CACHE_ENABLED: bool = True


def cache_get(key: str) -> Any | None:
    return _CACHE.get(key)


def cache_set(key: str, value: Any) -> None:
    _CACHE[key] = value
