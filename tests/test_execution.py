"""Execution模块测试"""
import sys
sys.path.insert(0, 'src')

from prometheus_omega.execution import Executor

def test_executor_init():
    """测试执行器初始化"""
    ex = Executor(max_workers=4)
    assert ex.max_workers == 4

def test_execute():
    """测试执行"""
    ex = Executor()
    result = ex.execute({'task': 'test'})
    assert result is not None

def test_submit():
    """测试提交"""
    ex = Executor()
    ex.submit({'task': 'test'})
    assert len(ex.queue) == 1

if __name__ == '__main__':
    test_executor_init()
    test_execute()
    test_submit()
    print("✅ All Execution tests passed!")
