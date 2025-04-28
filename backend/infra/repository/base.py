"""
Base repository for SQLAlchemy.

This module defines a base repository class `BaseSqlAlchemyRepository` which
provides common database operations using SQLAlchemy's `AsyncSession`. This
abstract class can be extended to implement specific repositories with custom
queries or operations.

Classes:
    BaseSqlAlchemyRepository: Abstract base class for SQLAlchemy repositories.

Methods:
    commit: Commits the current transaction to the database.
"""

from abc import ABC

from sqlalchemy.ext.asyncio import AsyncSession


class BaseSqlAlchemyRepository(ABC):
    """
    Abstract base repository class for SQLAlchemy ORM with async support.

    This class serves as a base for all repositories interacting with the
    SQLAlchemy `AsyncSession`. It provides a `commit` method for committing
    changes to the database.

    :param session: An instance of `AsyncSession` to interact with the database.
    :type session: AsyncSession
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def commit(self) -> None:
        """
        Commits the current transaction to the database.

        This method finalizes any pending changes in the current session
        and writes them to the database.

        :return: None
        """
        await self.session.commit()
