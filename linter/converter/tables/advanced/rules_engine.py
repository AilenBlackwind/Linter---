from typing import List, Dict, Any, Optional
from linter.converter.tables.advanced.models import ColorRule


class RuleTrigger:
    EQUALS = "equals"
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    MATCHES_REGEX = "matches_regex"


class RulesEngine:

    def __init__(self, rules: Optional[List[ColorRule]] = None):
        self._rules: List[ColorRule] = rules if rules else []
        self._sort_rules()

    def _sort_rules(self) -> None:
        self._rules.sort(key=lambda r: r.priority, reverse=True)

    @property
    def rules(self) -> List[ColorRule]:
        return self._rules

    def add_rule(self, rule: ColorRule) -> None:
        self._rules.append(rule)
        self._sort_rules()

    def remove_rule(self, rule: ColorRule) -> None:
        if rule in self._rules:
            self._rules.remove(rule)

    def clear_rules(self) -> None:
        self._rules.clear()

    def get_matching_rules(self, cell_text: str, col_idx: Optional[int] = None) -> List[ColorRule]:
        matching = []
        for rule in self._rules:
            if rule.matches(cell_text, col_idx):
                matching.append(rule)
        return matching

    def get_first_matching_rule(self, cell_text: str, col_idx: Optional[int] = None) -> Optional[ColorRule]:
        for rule in self._rules:
            if rule.matches(cell_text, col_idx):
                return rule
        return None

    def apply_rules(self, cell_text: str, base_style: Optional[Dict[str, Any]] = None, col_idx: Optional[int] = None) -> Dict[str, Any]:
        result = base_style.copy() if base_style else {}
        matching_rules = self.get_matching_rules(cell_text, col_idx)
        for rule in reversed(matching_rules):
            result = rule.apply_to_style(result)
        return result

    def apply_first_rule(self, cell_text: str, base_style: Optional[Dict[str, Any]] = None, col_idx: Optional[int] = None) -> Dict[str, Any]:
        result = base_style.copy() if base_style else {}
        rule = self.get_first_matching_rule(cell_text, col_idx)
        if rule:
            result = rule.apply_to_style(result)
        return result

    @classmethod
    def from_rules_list(cls, rules_data: List[dict]) -> 'RulesEngine':
        rules = []
        for data in rules_data:
            rule = ColorRule(
                name=data.get('name', ''),
                trigger=data.get('trigger', 'equals'),
                value=data.get('value', ''),
                case_sensitive=data.get('case_sensitive', False),
                shading=data.get('shading'),
                font_color=data.get('font_color'),
                bold=data.get('bold'),
                italic=data.get('italic'),
                priority=data.get('priority', 0),
            )
            rules.append(rule)
        return cls(rules)
