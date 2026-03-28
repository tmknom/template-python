"""Modelパッケージの公開API

Docs:
    - docs/specs/foundation/model/requirements.md
    - docs/specs/foundation/model/design.md
"""

from example.foundation.model.base import CoreModel, Field
from example.foundation.model.settings import CoreSettings, SettingsConfigDict

__all__ = ["CoreModel", "CoreSettings", "Field", "SettingsConfigDict"]
