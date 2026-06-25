"""Memory模块测试"""
import pytest
import sys
sys.path.insert(0, 'src')

from prometheus_omega.memory import MinervaStore, KeyNode, Bank

def test_minerva_insert():
    """测试插入"""
    store = MinervaStore()
    node = KeyNode(node_id='test', content='hello')
    result = store.insert(node)
    assert result == True

def test_minerva_retrieve():
    """测试检索"""
    store = MinervaStore()
    node = KeyNode(node_id='test', content='hello')
    store.insert(node)
    results = store.retrieve('test')
    assert len(results) >= 1

def test_bank_operations():
    """测试银行操作"""
    bank = Bank()
    bank.store('key', 'value')
    assert bank.retrieve('key') == 'value'
    assert bank.delete('key') == True
    assert bank.retrieve('key') is None

if __name__ == '__main__':
    test_minerva_insert()
    test_minerva_retrieve()
    test_bank_operations()
    print("✅ All Memory tests passed!")
