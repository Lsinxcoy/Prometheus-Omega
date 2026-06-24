"""Prometheus Ω - 边界测试"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest
import time


class TestBoundary(unittest.TestCase):
    def test_empty_content(self):
        from prometheus_omega.mechanisms.x_adapter import XMemoryAdapter
        adapter = XMemoryAdapter()
        entry_id = adapter.write("", importance=0.5)
        self.assertIsNotNone(entry_id)

    def test_very_long_content(self):
        from prometheus_omega.mechanisms.x_adapter import XMemoryAdapter
        adapter = XMemoryAdapter()
        long_content = "x" * 10000
        entry_id = adapter.write(long_content, importance=0.9)
        results = adapter.retrieve("x")
        self.assertGreater(len(results), 0)

    def test_concurrent_access(self):
        from prometheus_omega.store import SimpleCache
        import threading
        cache = SimpleCache(max_size=100, ttl=60)
        errors = []
        
        def writer(n):
            try:
                for i in range(10):
                    cache.set(f"key{n}_{i}", f"value{n}_{i}")
            except Exception as e:
                errors.append(e)
        
        threads = [threading.Thread(target=writer, args=(i,)) for i in range(10)]
        for t in threads: t.start()
        for t in threads: t.join()
        
        self.assertEqual(len(errors), 0)


class TestErrorHandling(unittest.TestCase):
    def test_cache_overflow(self):
        from prometheus_omega.store import SimpleCache
        cache = SimpleCache(max_size=3, ttl=60)
        cache.set("k1", "v1")
        cache.set("k2", "v2")
        cache.set("k3", "v3")
        cache.set("k4", "v4")
        self.assertIsNone(cache.get("k1"))

    def test_rate_limiter_reset(self):
        from prometheus_omega.evaluation import RateLimiter
        rl = RateLimiter(max_requests=2, window=0.1)
        self.assertTrue(rl.is_allowed())
        self.assertTrue(rl.is_allowed())
        self.assertFalse(rl.is_allowed())
        time.sleep(0.15)
        self.assertTrue(rl.is_allowed())


class TestPerformance(unittest.TestCase):
    def test_uuid_performance(self):
        from prometheus_omega import create_uuid
        import time
        start = time.time()
        for _ in range(1000):
            create_uuid()
        self.assertLess(time.time() - start, 1.0)

    def test_cache_performance(self):
        from prometheus_omega.store import SimpleCache
        import time
        cache = SimpleCache(max_size=1000)
        start = time.time()
        for i in range(1000):
            cache.set(f"key{i}", f"value{i}")
        for i in range(1000):
            cache.get(f"key{i}")
        self.assertLess(time.time() - start, 1.0)


if __name__ == '__main__':
    unittest.main(verbosity=2)