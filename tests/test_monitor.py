"""Monitor模块测试"""
import sys
sys.path.insert(0, 'src')

from prometheus_omega.monitor import HealthCheck

def test_health_check():
    """测试健康检查"""
    hc = HealthCheck()
    hc.register('test', lambda: True)
    result = hc.check()
    assert result == True

def test_health_check_fail():
    """测试健康检查失败"""
    hc = HealthCheck()
    hc.register('fail', lambda: False)
    result = hc.check()
    assert result == False

def test_get_status():
    """测试状态获取"""
    hc = HealthCheck()
    hc.register('ok', lambda: True)
    status = hc.get_status()
    assert 'ok' in status

if __name__ == '__main__':
    test_health_check()
    test_health_check_fail()
    test_get_status()
    print("✅ All Monitor tests passed!")
