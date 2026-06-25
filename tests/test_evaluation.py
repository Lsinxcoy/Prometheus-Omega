"""Evaluation模块测试"""
import pytest
import sys
sys.path.insert(0, 'src')

from prometheus_omega.evaluation import Evaluator, EvalResult

def test_evaluator_evaluate():
    """测试评估"""
    ev = Evaluator()
    result = ev.evaluate({})
    assert isinstance(result, EvalResult)
    assert 0 <= result.score <= 1

def test_evaluator_add_metric():
    """测试添加指标"""
    ev = Evaluator()
    def my_metric(c):
        return 0.8
    ev.add_metric('test_metric', my_metric)
    assert 'test_metric' in ev.metrics

if __name__ == '__main__':
    test_evaluator_evaluate()
    test_evaluator_add_metric()
    print("✅ All Evaluation tests passed!")
