from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Email(Base):
    __tablename__ = 'emails'

    id = Column(Integer, primary_key=True)
    gmail_id = Column(String, unique=True, nullable=False)
    thread_id = Column(String, nullable=False)
    from_address = Column(String, nullable=False)
    to_address = Column(String, nullable=False)
    subject = Column(String)
    message = Column(Text)
    received_date = Column(DateTime, nullable=False)
    is_read = Column(Boolean, default=False)
    label = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Email(id={self.id}, subject='{self.subject}')>"

class Rule(Base):
    __tablename__ = 'rules'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    predicate = Column(String, nullable=False)  # 'all' or 'any'
    priority = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    conditions = relationship("RuleCondition", back_populates="rule", cascade="all, delete-orphan")
    actions = relationship("RuleAction", back_populates="rule", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Rule(id={self.id}, name='{self.name}')>"

class RuleCondition(Base):
    __tablename__ = 'rule_conditions'

    id = Column(Integer, primary_key=True)
    rule_id = Column(Integer, ForeignKey('rules.id'), nullable=False)
    field = Column(String, nullable=False)  # 'from', 'subject', 'message', 'received_date'
    predicate = Column(String, nullable=False)  # 'contains', 'not_contains', 'equals', 'not_equals', 'less_than', 'greater_than'
    value = Column(String, nullable=False)
    rule = relationship("Rule", back_populates="conditions")

    def __repr__(self):
        return f"<RuleCondition(id={self.id}, field='{self.field}', predicate='{self.predicate}')>"

class RuleAction(Base):
    __tablename__ = 'rule_actions'

    id = Column(Integer, primary_key=True)
    rule_id = Column(Integer, ForeignKey('rules.id'), nullable=False)
    action_type = Column(String, nullable=False)  # 'mark_as_read', 'mark_as_unread', 'move_to'
    value = Column(String)  # For move_to action, this will be the label name
    rule = relationship("Rule", back_populates="actions")

    def __repr__(self):
        return f"<RuleAction(id={self.id}, action_type='{self.action_type}')>" 