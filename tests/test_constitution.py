"""Prometheus Ω - 宪法机制验证测试"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest


class TestConstitution(unittest.TestCase):
    def test_dopamine_gate(self):
        """测试多巴胺写入门控"""
        from prometheus_omega.z_mechanisms import DopamineWriteGate
        
        gate = DopamineWriteGate(threshold=0.2)
        
        # 高质量内容通过
        result = gate.can_write(0.9, 0.9, 0.9, 0.9)
        self.assertTrue(result)
        
        # 统计更新
        stats = gate.get_stats()
        self.assertIn('total_attempts', stats)
    
    def test_anti_evolution(self):
        """测试反演化门控"""
        from prometheus_omega.z_mechanisms import AntiEvolutionGate
        
        gate = AntiEvolutionGate(min_eval=0.7)
        
        # 高评估允许演化
        self.assertTrue(gate.can_evolve(0.8))
        # 低评估拒绝
        self.assertFalse(gate.can_evolve(0.5))
    
    def test_forgetting(self):
        """测试遗忘曲线"""
        from prometheus_omega.z_mechanisms import WeibullForgetting
        
        f = WeibullForgetting(scale=7.0)
        
        r1 = f.get_retention(0)
        r2 = f.get_retention(30)
        
        self.assertGreater(r1, r2)
    
    def test_convergence(self):
        """测试收敛检测"""
        from prometheus_omega.z_mechanisms import ConvergenceDetector
        
        d = ConvergenceDetector(threshold=0.1, window_size=3)
        
        d.check(0.9)
        d.check(0.91)
        result = d.check(0.905)
        
        self.assertIsInstance(result, bool)


if __name__ == '__main__':
    unittest.main(verbosity=2)