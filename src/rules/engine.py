from datetime import datetime, timedelta
from typing import List, Dict, Any
from ..database.models import Rule, RuleCondition, RuleAction, Email
from ..gmail.client import GmailClient

class RuleEngine:
    # Field mapping from rule field names to model attribute names
    FIELD_MAPPING = {
        'from': 'from_address',
        'to': 'to_address',
        'subject': 'subject',
        'message': 'message',
        'received_date': 'received_date',
        'is_read': 'is_read'
    }

    def __init__(self, gmail_client: GmailClient):
        self.gmail_client = gmail_client

    def evaluate_condition(self, email: Email, condition: RuleCondition) -> bool:
        """Evaluate a single condition against an email."""
        # Map the field name to the model attribute name
        field_name = self.FIELD_MAPPING.get(condition.field, condition.field)
        field_value = getattr(email, field_name)
        predicate = condition.predicate
        value = condition.value

        if condition.field == 'received_date':
            # Handle date comparisons
            try:
                if isinstance(value, str):
                    # Parse relative time (e.g., "7 days", "2 months")
                    amount, unit = value.split()
                    amount = int(amount)
                    if unit.lower() == 'days':
                        value = datetime.utcnow() - timedelta(days=amount)
                    elif unit.lower() == 'months':
                        value = datetime.utcnow() - timedelta(days=amount * 30)
                    else:
                        value = datetime.fromisoformat(value)

            except ValueError:
                return False

            if predicate == 'less_than':
                # For dates: if we want emails less than 2 days old, the email date should be greater than (more recent than) 2 days ago
                return field_value > value
            elif predicate == 'greater_than':
                # For dates: if we want emails greater than 2 days old, the email date should be less than (older than) 2 days ago
                return field_value < value
        else:
            # Handle string comparisons
            if not isinstance(field_value, str):
                field_value = str(field_value)
            
            if predicate == 'contains':
                return value.lower() in field_value.lower()
            elif predicate == 'not_contains':
                return value.lower() not in field_value.lower()
            elif predicate == 'equals':
                return value.lower() == field_value.lower()
            elif predicate == 'not_equals':
                return value.lower() != field_value.lower()

        return False

    def evaluate_rule(self, email: Email, rule: Rule) -> bool:
        """Evaluate all conditions of a rule against an email."""
        
        if not rule.conditions:
            return False
        if rule.predicate == 'all':
            return all(self.evaluate_condition(email, condition) for condition in rule.conditions)
        elif rule.predicate == 'any':
            return any(self.evaluate_condition(email, condition) for condition in rule.conditions)
        
        return False

    def execute_action(self, email: Email, action: RuleAction) -> bool:
        """Execute a single action on an email."""
        try:
            if action.action_type == 'mark_as_read':
                return self.gmail_client.mark_as_read(email.gmail_id)
            elif action.action_type == 'mark_as_unread':
                return self.gmail_client.mark_as_unread(email.gmail_id)
            elif action.action_type == 'move_to':
                return self.gmail_client.move_message(email.gmail_id, action.value)
            return False
        except Exception as e:
            print(f"Error executing action {action.action_type}: {e}")
            return False

    def process_email(self, email: Email, rules: List[Rule]) -> List[Dict[str, Any]]:
        """Process an email against all rules and return the results."""
        results = []
        
        for rule in rules:
            if self.evaluate_rule(email, rule):
                action_results = []
                for action in rule.actions:
                    success = self.execute_action(email, action)
                    action_results.append({
                        'action_type': action.action_type,
                        'value': action.value,
                        'success': success
                    })
                
                results.append({
                    'rule_name': rule.name,
                    'actions': action_results
                })
        
        return results 