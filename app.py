"""
app.py - Punto de entrada del Sistema de Recomendación de Cursos Online.

Orquesta la carga de datos, las reglas lógicas y el procesamiento funcional,
exponiéndolos a través de una API REST con Flask.
"""

import json
import os
from flask import Flask, request, jsonify

from models.curso import Curso
from processor.processor import procesar_recomendaciones, reducir_a_tags_unicos

app = Flask(__name__)

# Carga de datos y preparación del catálogo de cursos

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "cursos.json")

with open(DATA_PATH, encoding="utf-8") as f:
    _raw = json.load(f)

CATALOGO: list[Curso] = [Curso.from_dict(c) for c in _raw]


# Rutas de la API

@app.route("/", methods=["GET"])
def index():
    """Información general de la API."""
    return jsonify({
        "sistema": "Recomendador de Cursos Online",
        "version": "1.0",
        "rutas": {
            "GET  /cursos":         "Lista todos los cursos disponibles",
            "GET  /tags":           "Lista todos los tags únicos del catálogo",
            "POST /recomendar":     "Recibe preferencias y devuelve cursos recomendados",
        }
    })


@app.route("/cursos", methods=["GET"])
def listar_cursos():
    """Devuelve el catálogo completo de cursos."""
    return jsonify([c.to_dict() for c in CATALOGO])


@app.route("/tags", methods=["GET"])
def listar_tags():
    """Devuelve todos los tags únicos disponibles en el catálogo."""
    tags = reducir_a_tags_unicos(CATALOGO)
    return jsonify({"tags": tags})


@app.route("/recomendar", methods=["POST"])
def recomendar():
    """
    Recibe las preferencias del usuario y devuelve los cursos recomendados.

    Body JSON esperado:
    {
        "categoria":        "Programación",   (requerido)
        "nivel":            "Intermedio",      (requerido)
        "presupuesto_max":  100.0,             (requerido)
        "tiempo_disponible": 40,               (requerido)
        "modalidad":        "Asíncrono",       (requerido)
        "palabras_clave":   ["python", "web"], (opcional)
        "top_n":            5                  (opcional, default 5)
    }
    """
    datos = request.get_json(silent=True)

    if not datos:
        return jsonify({"error": "Se esperaba un body JSON."}), 400

    # Validar campos requeridos
    requeridos = ["categoria", "nivel", "presupuesto_max", "tiempo_disponible", "modalidad"]
    faltantes = [campo for campo in requeridos if campo not in datos]
    if faltantes:
        return jsonify({"error": f"Faltan los campos: {', '.join(faltantes)}"}), 400

    categoria        = datos["categoria"].strip()
    nivel            = datos["nivel"].strip()
    presupuesto_max  = float(datos["presupuesto_max"])
    tiempo_disponible = int(datos["tiempo_disponible"])
    modalidad        = datos["modalidad"].strip()
    palabras_clave   = datos.get("palabras_clave", [])
    top_n            = int(datos.get("top_n", 5))

    # Niveles compatibles (el usuario puede ver su nivel y el anterior)
    jerarquia = ["Principiante", "Intermedio", "Avanzado"]
    idx_nivel = jerarquia.index(nivel) if nivel in jerarquia else 0
    niveles_compatibles = jerarquia[: idx_nivel + 1]

    # Filtrar por categoria y nivel antes del pipeline funcional
    cursos_base = [
        c for c in CATALOGO
        if c.categoria.lower() == categoria.lower()
        and c.nivel in niveles_compatibles
    ]

    # Pipeline funcional: presupuesto → modalidad → tiempo → score → top N
    recomendados = procesar_recomendaciones(
        cursos=cursos_base,
        presupuesto=presupuesto_max,
        tiempo=tiempo_disponible,
        modalidad=modalidad,
        tags_usuario=palabras_clave,
        top_n=top_n,
    )

    # Si no hay resultados, aplicar relajacion
    if not recomendados:
        recomendados = procesar_recomendaciones(
            cursos=CATALOGO,
            presupuesto=presupuesto_max * 1.2,       # +20% presupuesto
            tiempo=tiempo_disponible,
            modalidad=modalidad,
            tags_usuario=palabras_clave,
            top_n=top_n,
        )
        modo = "relajado"
    else:
        modo = "estricto"

    # Separar altamente recomendados (rating >= 4.0)
    alta_recomendacion = [r for r in recomendados if r["curso"].rating >= 4.0]

    return jsonify({
        "modo": modo,
        "total_encontrados": len(recomendados),
        "alta_recomendacion": [
            {**r["curso"].to_dict(), "score": round(r["score"], 4)}
            for r in alta_recomendacion
        ],
        "recomendados": [
            {**r["curso"].to_dict(), "score": round(r["score"], 4)}
            for r in recomendados
        ],
    })


# para que arranque el servidor al ejecutar este script directamente

if __name__ == "__main__":
    print("=" * 50)
    print("  Sistema de Recomendación de Cursos Online")
    print(f"  Cursos cargados: {len(CATALOGO)}")
    print("  Servidor: http://127.0.0.1:5000")
    print("=" * 50)
    app.run(debug=True)