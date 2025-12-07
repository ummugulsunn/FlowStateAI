"""
User registration utilities for FlowStateAI.

Collects basic user information with lightweight validation and stores entries
as dictionaries inside an in-memory list.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


class ValidationError(ValueError):
    """Raised when provided user data fails validation."""


@dataclass
class UserRegistry:
    """
    Manage user registrations with minimal validation.

    Users are stored as dictionaries in an in-memory list. This is intended for
    early development and should be replaced with persistent storage as needed.
    """

    users: List[Dict[str, str]] = field(default_factory=list)

    @staticmethod
    def _validate_field(label: str, value: str) -> str:
        """
        Validate a string field ensuring it is not empty after stripping.

        Args:
            label: Name of the field for error messaging.
            value: Field value to validate.

        Returns:
            The cleaned string value.

        Raises:
            ValidationError: If the value is empty after trimming whitespace.
        """
        cleaned = value.strip()
        if not cleaned:
            raise ValidationError(f"{label} cannot be empty.")
        return cleaned

    def add_user(self, first_name: str, last_name: str, email: str) -> Dict[str, str]:
        """
        Add a user to the registry after basic validation.

        Args:
            first_name: User's first name.
            last_name: User's last name.
            email: User's email address.

        Returns:
            The registered user dictionary.

        Raises:
            ValidationError: If any field fails validation.
        """
        validated_first = self._validate_field("First name", first_name)
        validated_last = self._validate_field("Last name", last_name)
        validated_email = self._validate_field("Email", email)

        user_record = {
            "first_name": validated_first,
            "last_name": validated_last,
            "email": validated_email,
        }
        self.users.append(user_record)
        return user_record

    def list_users(self) -> List[Dict[str, str]]:
        """
        Return a copy of registered users.

        Returns:
            A shallow copy of the registered user dictionaries.
        """
        return list(self.users)


__all__ = ["UserRegistry", "ValidationError"]


