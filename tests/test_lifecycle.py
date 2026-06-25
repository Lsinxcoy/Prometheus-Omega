"""Lifecycle模块测试"""
import pytest
import sys
sys.path.insert(0, 'src')

from prometheus_omega.lifecycle import LifecycleManager

def test_lifecycle_tick():
    """测试tick方法"""
    lm = LifecycleManager()
    result = lm.tick()
    assert result is not None
    assert 'phase' in result

def test_lifecycle_initialization():
    """测试初始化"""
    lm = LifecycleManager()
    assert lm.phase is not None  # phase存在即可

if __name__ == '__main__':
    test_lifecycle_tick()
    test_lifecycle_initialization()
    print("✅ All Lifecycle tests passed!")
