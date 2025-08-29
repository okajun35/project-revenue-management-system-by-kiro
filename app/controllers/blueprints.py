from flask import Flask


def register_blueprints(app: Flask) -> None:
    """Register all Flask blueprints in one place.

    Keeping imports inside the function avoids circular import issues
    during application factory initialization.
    """
    from app.routes.main import main_bp  # noqa: WPS433
    from app.routes.projects import project_bp  # noqa: WPS433
    from app.routes.branches import branch_bp  # noqa: WPS433
    from app.routes.fiscal_years import fiscal_year_bp  # noqa: WPS433
    # I/O 系は io.py で一括公開
    from app.routes.io import export_bp, import_bp, backup_bp  # noqa: WPS433

    app.register_blueprint(main_bp)
    app.register_blueprint(project_bp)
    app.register_blueprint(branch_bp)
    app.register_blueprint(fiscal_year_bp)
    app.register_blueprint(export_bp)
    app.register_blueprint(import_bp)
    app.register_blueprint(backup_bp)
