"""
app.py - Punto de entrada del Sistema de Recomendacion de Cursos Online.

Implementa el patron Application Factory para Flask, permitiendo crear
la aplicacion de forma controlada y facilitando las pruebas unitarias.
"""

import os
from flask import Flask

# Registrar el Blueprint del controlador
from controller.controller import controller_bp


def crear_app() -> Flask:
    """
    Factory de la aplicacion Flask.

    Crea y configura la instancia de Flask con el punto de montaje
    correcto para templates y archivos estaticos, y registra el
    Blueprint del controlador.

    Returns:
        Flask: Instancia configurada de la aplicacion.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))

    app = Flask(
        __name__,
        template_folder=os.path.join(base_dir, "ui", "templates"),
        static_folder=os.path.join(base_dir, "ui", "static"),
    )

    # Clave secreta necesaria para flash messages
    app.secret_key = "clave_secreta_proyecto_lenguaje_2025"

    # Registrar el Blueprint del controlador
    app.register_blueprint(controller_bp)

    return app


if __name__ == "__main__":
    app = crear_app()
    print("=" * 50)
    print("  Sistema de Recomendacion de Cursos Online")
    print("  Abre tu navegador en: http://127.0.0.1:5000")
    print("=" * 50)
    app.run(debug=True)
