"""Rule engine for service validation"""

from dataclasses import dataclass
from typing import Callable, List, Tuple, Optional
import logging

# Import will be used for type hints
if False:  # TYPE_CHECKING equivalent
    from src.models.service import Service
    from src.models.device import Device
    from src.models.link import Link


logger = logging.getLogger(__name__)


@dataclass
class RuleCondition:
    """Represents a rule condition for service validation"""
    rule_id: str
    name: str
    condition: Callable[['Service', Optional['Device'], Optional['Link']], bool]
    action: str  # "reject" or "warn"
    enabled: bool = True
    priority: int = 0


class RuleEngine:
    """Rule engine for validating service provisioning requests"""
    
    def __init__(self):
        """Initialize the rule engine with an empty rules list"""
        self.rules: List[RuleCondition] = []
        self._initialize_default_rules()
    
    def _initialize_default_rules(self) -> None:
        """Initialize default validation rules"""
        # BW001: Bandwidth Capacity Check
        self.add_rule(RuleCondition(
            rule_id="BW001",
            name="Bandwidth Capacity Check",
            condition=lambda service, device, link: (
                device is not None and 
                service.bandwidth > device.calculate_available_capacity()
            ),
            action="reject",
            priority=1
        ))
        
        # LAT001: Latency Requirement Check
        self.add_rule(RuleCondition(
            rule_id="LAT001",
            name="Latency Requirement Check",
            condition=lambda service, device, link: (
                link is not None and
                service.latency_requirement is not None and 
                link.latency > service.latency_requirement
            ),
            action="reject",
            priority=2
        ))
    
    def add_rule(self, rule: RuleCondition) -> None:
        """
        Add a new rule to the engine and sort by priority
        
        Args:
            rule: RuleCondition object to add
        """
        self.rules.append(rule)
        # Sort rules by priority (lower priority number = higher precedence)
        self.rules.sort(key=lambda r: r.priority)
    
    def evaluate(self, service: 'Service', device: Optional['Device'] = None, 
                 link: Optional['Link'] = None) -> Tuple[bool, List[str]]:
        """
        Evaluate all enabled rules against a service request
        
        Args:
            service: Service object to validate
            device: Optional Device object for device-specific rules
            link: Optional Link object for link-specific rules
            
        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_violations)
                - is_valid: True if all rules pass, False otherwise
                - list_of_violations: List of violation messages
        """
        violations = []
        
        for rule in self.rules:
            if not rule.enabled:
                continue
            
            try:
                # Evaluate the rule condition
                if rule.condition(service, device, link):
                    if rule.action == "reject":
                        violation_msg = f"{rule.rule_id}: {rule.name}"
                        violations.append(violation_msg)
                        logger.warning(
                            f"Rule violation - {violation_msg} for service {service.id}"
                        )
            except Exception as e:
                error_msg = f"{rule.rule_id}: Error evaluating rule - {str(e)}"
                violations.append(error_msg)
                logger.error(
                    f"Rule evaluation error - {error_msg} for service {service.id}",
                    exc_info=True
                )
        
        is_valid = len(violations) == 0
        return is_valid, violations
