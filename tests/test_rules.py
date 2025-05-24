import pytest
from datetime import datetime, timedelta
from src.database.models import Email, Rule, RuleCondition, RuleAction
from src.rules.engine import RuleEngine
from src.gmail.client import GmailClient

@pytest.fixture
def sample_email():
    return Email(
        gmail_id="test123",
        thread_id="thread123",
        from_address="test@example.com",
        to_address="user@example.com",
        subject="Test Newsletter",
        message="This is a test newsletter",
        received_date=datetime.utcnow(),
        is_read=False
    )

@pytest.fixture
def sample_rule():
    rule = Rule(name="Test Rule", predicate="all")
    rule.conditions = [
        RuleCondition(
            field="subject",
            predicate="contains",
            value="newsletter"
        ),
        RuleCondition(
            field="from",
            predicate="contains",
            value="example.com"
        )
    ]
    rule.actions = [
        RuleAction(
            action_type="mark_as_read"
        ),
        RuleAction(
            action_type="move_to",
            value="Newsletters"
        )
    ]
    return rule

@pytest.fixture
def gmail_client():
    return GmailClient()

@pytest.fixture
def rule_engine(gmail_client):
    return RuleEngine(gmail_client)

def test_evaluate_condition(rule_engine, sample_email, sample_rule):
    # Test subject condition
    condition = sample_rule.conditions[0]
    assert rule_engine.evaluate_condition(sample_email, condition) is True

    # Test from condition
    condition = sample_rule.conditions[1]
    assert rule_engine.evaluate_condition(sample_email, condition) is True

    # Test negative case - change the from address to something that doesn't match
    sample_email.from_address = "other@domain.com"
    assert rule_engine.evaluate_condition(sample_email, condition) is False

def test_evaluate_rule(rule_engine, sample_email, sample_rule):
    # Test rule with all conditions matching
    assert rule_engine.evaluate_rule(sample_email, sample_rule) is True

    # Test rule with one condition not matching
    sample_email.subject = "Test Email"
    assert rule_engine.evaluate_rule(sample_email, sample_rule) is False

def test_date_condition(rule_engine, sample_email):
    # Test date condition
    condition = RuleCondition(
        field="received_date",
        predicate="less_than",
        value="7 days"
    )
    assert rule_engine.evaluate_condition(sample_email, condition) is True

    # Test old email
    sample_email.received_date = datetime.utcnow() - timedelta(days=10)
    assert rule_engine.evaluate_condition(sample_email, condition) is False

def test_any_predicate(rule_engine, sample_email):
    rule = Rule(name="Any Rule", predicate="any")
    rule.conditions = [
        RuleCondition(
            field="subject",
            predicate="contains",
            value="newsletter"
        ),
        RuleCondition(
            field="subject",
            predicate="contains",
            value="nonexistent"
        )
    ]
    
    # Test with one matching condition
    assert rule_engine.evaluate_rule(sample_email, rule) is True

    # Test with no matching conditions
    sample_email.subject = "Test Email"
    assert rule_engine.evaluate_rule(sample_email, rule) is False 