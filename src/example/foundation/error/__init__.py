"""Errorパッケージの公開API

Docs:
    - docs/specs/foundation/error/requirements.md
    - docs/specs/foundation/error/design.md
"""

from example.foundation.error.error import ApplicationError
from example.foundation.error.handler import ErrorHandler

__all__ = [
    "ApplicationError",
    "ErrorHandler",
]
