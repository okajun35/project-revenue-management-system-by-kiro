from flask import Flask, jsonify, render_template, request
from werkzeug.exceptions import HTTPException


def register_error_handlers(app: Flask) -> None:
    """Register global error handlers for both JSON and HTML responses."""

    @app.errorhandler(HTTPException)
    def handle_http_exception(e: HTTPException):  # type: ignore
        wants_json = request.accept_mimetypes.best == 'application/json' or request.path.startswith('/api/')
        if wants_json:
            return jsonify(error=e.name, message=e.description), e.code
        return (
            render_template('errors/error.html', code=e.code, name=e.name, description=e.description),
            e.code,
        )

    @app.errorhandler(Exception)
    def handle_exception(e: Exception):  # type: ignore
        app.logger.exception(e)
        wants_json = request.accept_mimetypes.best == 'application/json' or request.path.startswith('/api/')
        if wants_json:
            return jsonify(error='Internal Server Error'), 500
        return render_template('errors/500.html'), 500
