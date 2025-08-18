"""
I/O 系機能（Import/Export/Backup）の Blueprint を一括で公開するモジュール。

Import/Export は app.routes.* の新実装を参照し、Backup は暫定的に旧実装を参照します。
"""

from app.routes.importing import import_bp  # noqa: F401
from app.routes.export import export_bp  # noqa: F401
from app.routes.backup import backup_bp  # noqa: F401

__all__ = ["import_bp", "export_bp", "backup_bp"]
