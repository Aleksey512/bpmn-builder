"""
SQLAlchemy declarative base module.

This module defines the declarative base class used for creating ORM models.
All SQLAlchemy ORM models should inherit from `Base`.

:var Base: Declarative base class for SQLAlchemy models.
"""

from sqlalchemy.orm import declarative_base

Base = declarative_base()
