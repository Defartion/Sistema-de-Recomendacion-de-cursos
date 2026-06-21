"""
Modulo controlador (paradigma imperativo/OO).

Este modulo orquesta las peticiones HTTP, coordina el llamado a los 
modulos funcionales y logicos, y renderiza las vistas correspondientes.
Implementa el flujo de control imperativo: recepcion, validacion,
procesamiento y respuesta.
"""

import json
import logging
import os
from typing import List

from flask import Blueprint, render_template, request, flash, redirect, url_for

from models.curso import Curso
from processor.processor import procesar_recomendaciones
from logic_rules.logic_rules import inferir_recomendaciones


# Configuracion de logging (solo en el controlador, no en modulos puros)
logger = logging.getLogger(__name__)

# Blueprint de Flask para organizar las rutas
controller_bp = Blueprint("controller", __name__, template_folder="ui/templates")

# Carga de base de conocimiento al iniciar (imperativo: estado mutable controlado)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CURSOS_JSON = os.path.join(BASE_DIR, "data", "cursos.json")

_catalogo_cursos: List[Curso] = []


def _cargar_catalogo() -> List[Curso]:
    """Carga el catalogo de cursos desde el archivo JSON."""
    global _catalogo_cursos
    if not _catalogo_cursos:
        with open(CURSOS_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
        _catalogo_cursos = [Curso.from_dict(c) for c in data]
    return _catalogo_cursos


@controller_bp.route("/")
def index():
    """Ruta principal: muestra el formulario de preferencias."""
    logger.info("Solicitud GET a la pagina principal")
    return render_template("index.html")


@controller_bp.route("/recomendar", methods=["POST"])
def recomendar():
    """Ruta de recomendacion: procesa preferencias y muestra resultados."""
    try:
        # Recoleccion de datos del formulario (imperativo)
        categoria = request.form.get("categoria", "").strip()
        nivel = request.form.get("nivel", "").strip()
        presupuesto = request.form.get("presupuesto", "0")
        tiempo = request.form.get("tiempo", "0")
        modalidad = request.form.get("modalidad", "").strip()
        tags = request.form.get("tags", "").strip()

        logger.info(
            f"Solicitud de recomendacion: categoria={categoria}, nivel={nivel}, "
            f"presupuesto={presupuesto}, tiempo={tiempo}, modalidad={modalidad}"
        )

        # Validacion de campos obligatorios
        if not all([categoria, nivel, presupuesto, tiempo, modalidad]):
            flash("Por favor completa todos los campos obligatorios.", "error")
            return redirect(url_for("controller.index"))

        # Conversion y validacion de tipos
        try:
            presupuesto_val = float(presupuesto)
            tiempo_val = int(tiempo)
        except ValueError:
            flash("Los valores de presupuesto y tiempo deben ser numericos.", "error")
            return redirect(url_for("controller.index"))

        if presupuesto_val < 0 or tiempo_val <= 0:
            flash("El presupuesto debe ser positivo y el tiempo mayor a 0.", "error")
            return redirect(url_for("controller.index"))

        # Procesamiento de tags
        tags_list = [t.strip() for t in tags.split(",") if t.strip()]

        # Carga del catalogo
        catalogo = _cargar_catalogo()

        # Paso 1: Inferencia logica (paradigma logico)
        preferencias = {
            "categoria": categoria,
            "nivel": nivel,
            "presupuesto_max": presupuesto_val,
            "tiempo_disponible": tiempo_val,
        }
        recomendados_logicos, altamente_recomendados = inferir_recomendaciones(
            preferencias, catalogo
        )

        # Paso 2: Procesamiento funcional (paradigma funcional)
        resultados_funcionales = procesar_recomendaciones(
            catalogo, presupuesto=presupuesto_val, tiempo=tiempo_val,
            modalidad=modalidad, tags_usuario=tags_list, top_n=10
        )

        # Paso 3: Combinacion de resultados (logica imperativa)
        # Priorizar los que estan en ambas listas
        ids_logicos = {c.id for c in recomendados_logicos}
        ids_altos = {c.id for c in altamente_recomendados}

        combinados = []
        for res in resultados_funcionales:
            curso = res["curso"]
            combinados.append({
                "curso": curso,
                "score": res["score"],
                "es_logico": curso.id in ids_logicos,
                "es_alto": curso.id in ids_altos,
            })

        # Ordenar: primero altamente recomendados, luego por score
        combinados.sort(
            key=lambda x: (not x["es_alto"], -x["score"])
        )

        return render_template(
            "resultado.html",
            recomendaciones=combinados,
            preferencias={
                "categoria": categoria,
                "nivel": nivel,
                "presupuesto": presupuesto_val,
                "tiempo": tiempo_val,
                "modalidad": modalidad,
                "tags": tags_list,
            }
        )

    except Exception as e:
        # Manejo de excepciones (paradigma imperativo: control de flujo de errores)
        logger.error(f"Error al procesar recomendacion: {e}")
        flash(f"Ocurrio un error al procesar la solicitud: {str(e)}", "error")
        return redirect(url_for("controller.index"))
