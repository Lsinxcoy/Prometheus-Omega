"""Store模块测试"""
import pytest
import sys
sys.path.insert(0, 'src')

from prometheus_omega.store import Store, InMemoryStorage

def test_store_basic():
    """测试Store基本读写"""
    s = Store()
    s.set('key1', 'value1')
    assert s.get('key1') == 'value1'

def test_store_overwrite():
    """测试覆盖写入"""
    s = Store()
    s.set('key', 'v1')
    s.set('key', 'v2')
    assert s.get('key') == 'v2'

def test_store_delete():
    """测试删除"""
    s = Store()
    s.set('key', 'value')
    s.delete('key')
    assert s.get('key') is None

def test_inmemory_storage():
    """测试内存存储"""
    store = InMemoryStorage()
    store.set('k', 'v')
    assert store.get('k') == 'v'
    assert store.delete('k') == True

def test_store_constitution_gate():
    """测试宪法门控"""
    s = Store()
    # 默认可以写入
    result = s.set('test', 'value')
    assert result == True

if __name__ == '__main__':
    test_store_basic()
    test_store_overwrite()
    test_store_delete()
    test_inmemory_storage()
    test_store_constitution_gate()
    print("✅ All Store tests passed!")
