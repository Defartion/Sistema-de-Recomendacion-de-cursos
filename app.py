"""
Punto de entrada de la aplicacion Flask.

Este modulo inicializa la aplicacion web y registra el blueprint del 
controlador principal.
"""

from flask import Flask
from controller.controller import controller_bp


def crear_app() -> Flask:
    """Factory de la aplicacion Flask."""
    app = Flask(
        __name__,
        template_folder="ui/templates",
        static_folder="ui/static",
    )
    app.secret_key = "clave-secreta-desarrollo-lp-2024"
    app.register_blueprint(controller_bp)
    return app


app = crear_app()

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
