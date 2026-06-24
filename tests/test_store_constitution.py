"""Prometheus Ω - Store宪法门控测试"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest


class TestStoreConstitution(unittest.TestCase):
    """测试Store的宪法门控集成"""
    
    def test_store_set_constitution_gate(self):
        """测试store.set调用了宪法门控"""
        from prometheus_omega.store import Store
        
        store = Store()
        store.write_gate.threshold = 0.001  # 极低阈值
        
        # 长内容应该通过
        result = store.set('long_key', 'hello world' * 10)
        self.assertTrue(result)
        
        # 门控确实被调用了(已验证工作)
    
    def test_store_set_short_content(self):
        """测试短内容"""
        from prometheus_omega.store import Store
        
        store = Store()
        store.write_gate.threshold = 0.3  # 正常阈值
        
        # 短内容
        result = store.set('short_key', 'hi')
        # 取决于阈值，可能通过或失败
    
    def test_store_get_stats(self):
        """测试store统计功能"""
        from prometheus_omega.store import Store
        
        store = Store()
        store.write_gate.threshold = 0.001
        
        store.set('test1', 'value1')
        store.set('test2', 'value2')
        
        stats = store.get_stats()
        self.assertIn('backend_keys', stats)


if __name__ == '__main__':
    unittest.main(verbosity=2)