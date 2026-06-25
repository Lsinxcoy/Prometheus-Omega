"""Safety宪法门控测试"""
import pytest
import sys
sys.path.insert(0, 'src')

from prometheus_omega.safety import DopamineWriteGate, AntiEvolutionGate

def test_dopamine_write_gate_high_quality():
    """高质量应该允许写入"""
    dwg = DopamineWriteGate(threshold=0.1)
    result = dwg.can_write(1.0, 1.0, 1.0)
    assert result == True

def test_dopamine_write_gate_low_quality():
    """低质量应该拒绝写入"""
    dwg = DopamineWriteGate(threshold=0.3)
    result = dwg.can_write(0.1, 0.1, 0.1)
    assert result == False

def test_dopamine_write_gate_low_dopamine():
    """低多巴胺应该拒绝写入"""
    dwg = DopamineWriteGate(threshold=0.1, min_dopamine=0.5)
    result = dwg.can_write(1.0, 1.0, 1.0, dopamine=0.3)
    assert result == False

def test_anti_evolution_normal():
    """正常情况应该允许进化"""
    aeg = AntiEvolutionGate(energy_threshold=0.9)
    result = aeg.can_evolve(energy_used=0.3, total_energy=1.0)
    assert result == True

def test_anti_evolution_over_energy():
    """超能量应该拒绝"""
    aeg = AntiEvolutionGate(energy_threshold=0.5)
    result = aeg.can_evolve(energy_used=0.6, total_energy=1.0)
    assert result == False

def test_anti_evolution_high_risk():
    """高风险应该拒绝"""
    aeg = AntiEvolutionGate(risk_threshold=0.3)
    result = aeg.can_evolve(0.3, 1.0, 0.1, 0.5)
    assert result == False

if __name__ == '__main__':
    test_dopamine_write_gate_high_quality()
    test_dopamine_write_gate_low_quality()
    test_dopamine_write_gate_low_dopamine()
    test_anti_evolution_normal()
    test_anti_evolution_over_energy()
    test_anti_evolution_high_risk()
    print("✅ All Safety tests passed!")
