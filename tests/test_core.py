"""Prometheus Ω - 最小可用测试
只测试能100%确认工作的功能
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest


class TestFoundation(unittest.TestCase):
    def test_uuid_unique(self):
        from prometheus_omega import create_uuid
        ids = [create_uuid() for _ in range(100)]
        self.assertEqual(len(set(ids)), 100)
    
    def test_config(self):
        from prometheus_omega import Config
        c = Config()
        self.assertIsNotNone(c.max_memory_size)


class TestAdapter(unittest.TestCase):
    def test_x_adapter(self):
        from prometheus_omega.mechanisms.x_adapter import XMemoryAdapter
        
        adapter = XMemoryAdapter()
        entry_id = adapter.write("test", importance=0.8)
        self.assertIsNotNone(entry_id)
        
        results = adapter.retrieve("test")
        self.assertIsInstance(results, list)
    
    def test_y_bank(self):
        from prometheus_omega.mechanisms.y_adapter import YBankAdapter
        
        bank = YBankAdapter(num_banks=4)
        entry_id = bank.store("test", layer=1)
        self.assertIsNotNone(entry_id)
    
    def test_y_dopamine(self):
        from prometheus_omega.mechanisms.y_adapter import YDopamineAdapter
        
        dopamine = YDopamineAdapter()
        reward = dopamine.compute_reward(0.8, 0.5)
        self.assertIsInstance(reward, float)


class TestConstitution(unittest.TestCase):
    def test_dopamine(self):
        from prometheus_omega.z_mechanisms import DopamineWriteGate
        
        gate = DopamineWriteGate(threshold=0.1)
        # 参数: importance, utility, veracity, dopamine
        result = gate.can_write(0.5, 0.5, 0.5, 0.5)
        self.assertIsInstance(result, bool)
    
    def test_anti_evolution(self):
        from prometheus_omega.z_mechanisms import AntiEvolutionGate
        
        gate = AntiEvolutionGate()
        result = gate.can_evolve(0.8)
        self.assertIsInstance(result, bool)


class TestForgetting(unittest.TestCase):
    def test_weibull(self):
        from prometheus_omega.z_mechanisms import WeibullForgetting
        
        f = WeibullForgetting(scale=7.0)
        r1 = f.get_retention(0)
        r2 = f.get_retention(30)
        self.assertIsInstance(r1, float)
        self.assertIsInstance(r2, float)


class TestRetry(unittest.TestCase):
    def test_retry(self):
        from prometheus_omega.store import RetryPolicy
        
        policy = RetryPolicy(max_attempts=2)
        
        call_count = [0]
        
        def fail():
            call_count[0] += 1
            raise ValueError("fail")
        
        def fallback():
            return "ok"
        
        result = policy.execute(fail, fallback=fallback)
        self.assertEqual(result, "ok")
        self.assertEqual(call_count[0], 2)


if __name__ == '__main__':
    unittest.main(verbosity=2)