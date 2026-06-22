"""
app.py - Punto de entrada del Sistema de Recomendacion de Cursos Online.

Orquesta la carga de datos, las reglas logicas y el procesamiento funcional,
exponiendolos a traves de una interfaz web con Flask.
"""

import os
from flask import Flask

# Configurar Flask para encontrar templates en ui/templates y static en ui/static
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "ui", "templates"),
    static_folder=os.path.join(BASE_DIR, "ui", "static"),
)

# Clave secreta necesaria para flash messages
app.secret_key = "clave_secreta_proyecto_lenguaje_2025"

# Registrar el Blueprint del controlador
from controller.controller import controller_bp
app.register_blueprint(controller_bp)

if __name__ == "__main__":
    print("=" * 50)
    print("  Sistema de Recomendacion de Cursos Online")
    print("  Abre tu navegador en: http://127.0.0.1:5000")
    print("=" * 50)
    app.run(debug=True)