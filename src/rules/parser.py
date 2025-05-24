# src/rules/parser.py
import json
import os
from src.database.models import Rule, RuleCondition, RuleAction
from sqlalchemy.orm import joinedload

class RuleParser:
    def __init__(self, rules_file):
        self.rules_file = rules_file

    def get_rules_from_db(self, db):
        """Fetches rules from the database, eagerly loading their conditions and actions."""
        return db.query(Rule).options(
            joinedload(Rule.conditions),
            joinedload(Rule.actions)
        ).all()

    def save_rules_to_db(self, db):
        """
        Loads rules from the JSON file, saves/updates them in the database,
        and ensures they are bound to the provided session.
        """
        if not os.path.exists(self.rules_file):
            print(f"Error: Rule file not found at {self.rules_file}")
            return []

        with open(self.rules_file, 'r') as f:
            rules_data = json.load(f)

        saved_rules = []
        for rule_data in rules_data.get('rules', []):
            rule_name = rule_data.get('name')
            if not rule_name:
                print(f"Warning: Rule data missing 'name': {rule_data}")
                continue

            # Try to find an existing rule by name
            rule = db.query(Rule).filter_by(name=rule_name).first()

            if rule:
                # Update existing rule's fields
                rule.priority = rule_data.get('priority', 0)
                rule.predicate = rule_data.get('predicate', 'all')  # Default to 'all' if not specified
                
                # Clear existing conditions and actions
                db.query(RuleCondition).filter_by(rule_id=rule.id).delete()
                db.query(RuleAction).filter_by(rule_id=rule.id).delete()
                db.refresh(rule)
            else:
                # Create a new rule with all required fields
                rule = Rule(
                    name=rule_name,
                    priority=rule_data.get('priority', 0),
                    predicate=rule_data.get('predicate', 'all')  # Default to 'all' if not specified
                )
                db.add(rule)

            # Add new conditions for the rule
            for cond_data in rule_data.get('conditions', []):
                condition = RuleCondition(
                    field=cond_data.get('field'),
                    predicate=cond_data.get('predicate'),
                    value=cond_data.get('value')
                )
                if condition.field and condition.predicate and condition.value is not None:
                    rule.conditions.append(condition)
                else:
                    print(f"Warning: Skipping malformed condition for rule '{rule_name}': {cond_data}")

            # Add new actions for the rule
            for action_data in rule_data.get('actions', []):
                action = RuleAction(
                    action_type=action_data.get('type'),
                    value=action_data.get('value')
                )
                if action.action_type:
                    rule.actions.append(action)
                else:
                    print(f"Warning: Skipping malformed action for rule '{rule_name}': {action_data}")

            saved_rules.append(rule)

        db.commit()
        
        # Re-query rules with eager loading for both conditions and actions
        rule_ids = [r.id for r in saved_rules if r.id]
        if rule_ids:
            return db.query(Rule).filter(Rule.id.in_(rule_ids)).options(
                joinedload(Rule.conditions),
                joinedload(Rule.actions)
            ).all()
        return []