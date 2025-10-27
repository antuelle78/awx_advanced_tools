from app.llm.cache import cache_get, cache_set, CACHE_ENABLED


class TestLLMCache:
    def test_cache_set_and_get(self):
        cache_set("key1", "value1")
        assert cache_get("key1") == "value1"
        assert cache_get("nonexistent") is None

    def test_cache_enabled(self):
        assert CACHE_ENABLED is True

    def test_cache_overwrite(self):
        cache_set("key1", "value1")
        cache_set("key1", "value2")
        assert cache_get("key1") == "value2"
