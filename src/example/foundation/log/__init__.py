"""Logパッケージの公開API

Docs:
    - docs/specs/foundation/log/requirements.md
    - docs/specs/foundation/log/design.md
"""

from example.foundation.log.configurator import LogConfigurator
from example.foundation.log.decorator import log

__all__ = ["LogConfigurator", "log"]
