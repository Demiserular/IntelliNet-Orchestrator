"""Unit tests for rule engine"""

import pytest
from src.services.rule_engine import RuleEngine, RuleCondition
from src.models.service import Service, ServiceType
from src.models.device import Device, DeviceType
from src.models.link import Link, LinkType
from src.models.specialized_devices import MPLSRouter


class TestRuleCondition:
    """Tests for RuleCondition dataclass"""
    
    def test_rule_condition_creation(self):
        """Test creating a RuleCondition"""
        rule = RuleCondition(
            rule_id="TEST001",
            name="Test Rule",
            condition=lambda s, d, l: True,
            action="reject",
            enabled=True,
            priority=1
        )
        
        assert rule.rule_id == "TEST001"
        assert rule.name == "Test Rule"
        assert rule.action == "reject"
        assert rule.enabled is True
        assert rule.priority == 1


class TestRuleEngine:
    """Tests for RuleEngine class"""
    
    def test_rule_engine_initialization(self):
        """Test that RuleEngine initializes with default rules"""
        engine = RuleEngine()
        
        # Should have 2 default rules (BW001 and LAT001)
        assert len(engine.rules) == 2
        assert engine.rules[0].rule_id == "BW001"
        assert engine.rules[1].rule_id == "LAT001"
    
    def test_add_rule(self):
        """Test adding a rule to the engine"""
        engine = RuleEngine()
        initial_count = len(engine.rules)
        
        new_rule = RuleCondition(
            rule_id="TEST001",
            name="Test Rule",
            condition=lambda s, d, l: False,
            action="reject",
            priority=10
        )
        
        engine.add_rule(new_rule)
        
        assert len(engine.rules) == initial_count + 1
        assert new_rule in engine.rules
    
    def test_rule_priority_sorting(self):
        """Test that rules are sorted by priority"""
        engine = RuleEngine()
        
        # Add rules with different priorities
        rule_high = RuleCondition(
            rule_id="HIGH",
            name="High Priority",
            condition=lambda s, d, l: False,
            action="reject",
            priority=0
        )
        
        rule_low = RuleCondition(
            rule_id="LOW",
            name="Low Priority",
            condition=lambda s, d, l: False,
            action="reject",
            priority=100
        )
        
        engine.add_rule(rule_low)
        engine.add_rule(rule_high)
        
        # High priority (lower number) should come first
        assert engine.rules[0].rule_id == "HIGH"
    
    def test_evaluate_passing_conditions(self):
        """Test rule evaluation with passing conditions"""
        engine = RuleEngine()
        
        # Create a service with sufficient bandwidth
        service = Service(
            id="S1",
            service_type=ServiceType.MPLS_VPN,
            source_device_id="D1",
            target_device_id="D2",
            bandwidth=50.0
        )
        
        # Create a device with sufficient capacity
        device = MPLSRouter(
            id="D1",
            name="Router1",
            capacity=100.0
        )
        
        is_valid, violations = engine.evaluate(service, device=device)
        
        assert is_valid is True
        assert len(violations) == 0
    
    def test_evaluate_failing_bandwidth_rule(self):
        """Test rule evaluation with bandwidth capacity violation"""
        engine = RuleEngine()
        
        # Create a service requesting more bandwidth than available
        service = Service(
            id="S1",
            service_type=ServiceType.MPLS_VPN,
            source_device_id="D1",
            target_device_id="D2",
            bandwidth=150.0
        )
        
        # Create a device with insufficient capacity
        device = MPLSRouter(
            id="D1",
            name="Router1",
            capacity=100.0
        )
        
        is_valid, violations = engine.evaluate(service, device=device)
        
        assert is_valid is False
        assert len(violations) == 1
        assert "BW001" in violations[0]
        assert "Bandwidth Capacity Check" in violations[0]
    
    def test_evaluate_failing_latency_rule(self):
        """Test rule evaluation with latency requirement violation"""
        engine = RuleEngine()
        
        # Create a service with strict latency requirement
        service = Service(
            id="S1",
            service_type=ServiceType.MPLS_VPN,
            source_device_id="D1",
            target_device_id="D2",
            bandwidth=50.0,
            latency_requirement=5.0  # 5ms max
        )
        
        # Create a link with high latency
        link = Link(
            id="L1",
            source_device_id="D1",
            target_device_id="D2",
            bandwidth=100.0,
            link_type=LinkType.FIBER,
            latency=10.0  # 10ms actual
        )
        
        is_valid, violations = engine.evaluate(service, link=link)
        
        assert is_valid is False
        assert len(violations) == 1
        assert "LAT001" in violations[0]
        assert "Latency Requirement Check" in violations[0]
    
    def test_evaluate_multiple_rule_violations(self):
        """Test rule evaluation with multiple violations"""
        engine = RuleEngine()
        
        # Create a service with high bandwidth and strict latency
        service = Service(
            id="S1",
            service_type=ServiceType.MPLS_VPN,
            source_device_id="D1",
            target_device_id="D2",
            bandwidth=150.0,
            latency_requirement=5.0
        )
        
        # Create a device with insufficient capacity
        device = MPLSRouter(
            id="D1",
            name="Router1",
            capacity=100.0
        )
        
        # Create a link with high latency
        link = Link(
            id="L1",
            source_device_id="D1",
            target_device_id="D2",
            bandwidth=100.0,
            link_type=LinkType.FIBER,
            latency=10.0
        )
        
        is_valid, violations = engine.evaluate(service, device=device, link=link)
        
        assert is_valid is False
        assert len(violations) == 2
        assert any("BW001" in v for v in violations)
        assert any("LAT001" in v for v in violations)
    
    def test_evaluate_disabled_rule_exclusion(self):
        """Test that disabled rules are not evaluated"""
        engine = RuleEngine()
        
        # Disable the bandwidth rule
        for rule in engine.rules:
            if rule.rule_id == "BW001":
                rule.enabled = False
        
        # Create a service that would violate bandwidth rule
        service = Service(
            id="S1",
            service_type=ServiceType.MPLS_VPN,
            source_device_id="D1",
            target_device_id="D2",
            bandwidth=150.0
        )
        
        device = MPLSRouter(
            id="D1",
            name="Router1",
            capacity=100.0
        )
        
        is_valid, violations = engine.evaluate(service, device=device)
        
        # Should pass because the rule is disabled
        assert is_valid is True
        assert len(violations) == 0
    
    def test_evaluate_with_rule_exception(self):
        """Test error handling when rule condition raises exception"""
        engine = RuleEngine()
        
        # Add a rule that will raise an exception
        def faulty_condition(service, device, link):
            raise ValueError("Intentional error")
        
        faulty_rule = RuleCondition(
            rule_id="FAULT001",
            name="Faulty Rule",
            condition=faulty_condition,
            action="reject",
            priority=0
        )
        
        engine.add_rule(faulty_rule)
        
        service = Service(
            id="S1",
            service_type=ServiceType.MPLS_VPN,
            source_device_id="D1",
            target_device_id="D2",
            bandwidth=50.0
        )
        
        is_valid, violations = engine.evaluate(service)
        
        # Should capture the exception as a violation
        assert is_valid is False
        assert len(violations) >= 1
        assert any("FAULT001" in v and "Error evaluating rule" in v for v in violations)
    
    def test_evaluate_without_optional_parameters(self):
        """Test evaluation when device or link are None"""
        engine = RuleEngine()
        
        service = Service(
            id="S1",
            service_type=ServiceType.MPLS_VPN,
            source_device_id="D1",
            target_device_id="D2",
            bandwidth=50.0
        )
        
        # Should not raise exception when device and link are None
        is_valid, violations = engine.evaluate(service)
        
        # Should pass because rules check for None
        assert is_valid is True
        assert len(violations) == 0
