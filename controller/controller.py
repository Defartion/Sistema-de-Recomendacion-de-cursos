"""
Modulo controlador (paradigma imperativo/OO).

Este modulo orquesta las peticiones HTTP, coordina el llamado a los 
modulos funcionales y logicos, y renderiza las vistas correspondientes.
"""

import json
import logging
import os
from typing import List

from flask import Blueprint, render_template, request, flash, redirect, url_for

from models.curso import Curso
from processor.processor import procesar_recomendaciones
from logic_rules.logic_rules import inferir_recomendaciones

logger = logging.getLogger(__name__)

controller_bp = Blueprint("controller", __name__, template_folder="ui/templates")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CURSOS_JSON = os.path.join(BASE_DIR, "data", "cursos.json")

_catalogo_cursos: List[Curso] = []


def _cargar_catalogo() -> List[Curso]:
    global _catalogo_cursos
    if not _catalogo_cursos:
        with open(CURSOS_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
        _catalogo_cursos = [Curso.from_dict(c) for c in data]
    return _catalogo_cursos


# Mapa de profesion -> categorias relacionadas
PROFESION_CATEGORIA = {
    "ingenieria": ["Programacion", "Datos"],
    "sistemas": ["Programacion", "Datos"],
    "software": ["Programacion", "Datos"],
    "informatica": ["Programacion", "Datos"],
    "computacion": ["Programacion", "Datos"],
    "medicina": ["Datos"],
    "salud": ["Datos"],
    "administracion": ["Negocios", "Marketing"],
    "negocios": ["Negocios", "Marketing"],
    "empresa": ["Negocios", "Marketing"],
    "marketing": ["Marketing"],
    "publicidad": ["Marketing"],
    "diseno": ["Diseno"],
    "arte": ["Diseno"],
    "grafico": ["Diseno"],
    "idiomas": ["Idiomas"],
    "traduccion": ["Idiomas"],
    "lenguas": ["Idiomas"],
    "datos": ["Datos"],
    "estadistica": ["Datos"],
    "economia": ["Negocios", "Datos"],
    "contabilidad": ["Negocios"],
    "finanzas": ["Negocios", "Datos"],
}


def _categorias_por_profesion(profesion: str) -> List[str]:
    """Infiere categorias relacionadas a la profesion del usuario."""
    profesion_lower = profesion.lower()
    categorias = []
    for keyword, cats in PROFESION_CATEGORIA.items():
        if keyword in profesion_lower:
            for cat in cats:
                if cat not in categorias:
                    categorias.append(cat)
    return categorias


@controller_bp.route("/")
def index():
    logger.info("Solicitud GET a la pagina principal")
    return render_template("index.html")


@controller_bp.route("/recomendar", methods=["POST"])
def recomendar():
    try:
        # Datos del formulario — campos nuevos del onboarding
        nombre    = request.form.get("nombre", "").strip()
        edad      = request.form.get("edad", "").strip()
        sexo      = request.form.get("sexo", "").strip()
        profesion = request.form.get("profesion", "").strip()

        # Campos de preferencias
        categoria  = request.form.get("categoria", "").strip()
        nivel      = request.form.get("nivel", "").strip()
        presupuesto = request.form.get("presupuesto", "0")
        tiempo     = request.form.get("tiempo", "0")
        modalidad  = request.form.get("modalidad", "").strip()
        tags       = request.form.get("tags", "").strip()

        logger.info(
            f"Recomendacion para: {nombre}, profesion={profesion}, "
            f"categoria={categoria}, nivel={nivel}, modalidad={modalidad}"
        )

        # Validacion de campos obligatorios
        if not all([categoria, nivel, presupuesto, tiempo, modalidad]):
            flash("Por favor completa todos los campos obligatorios.", "error")
            return redirect(url_for("controller.index"))

        try:
            presupuesto_val = float(presupuesto)
            tiempo_val = int(tiempo)
        except ValueError:
            flash("Los valores de presupuesto y tiempo deben ser numericos.", "error")
            return redirect(url_for("controller.index"))

        if presupuesto_val < 0 or tiempo_val <= 0:
            flash("El presupuesto debe ser positivo y el tiempo mayor a 0.", "error")
            return redirect(url_for("controller.index"))

        tags_list = [t.strip() for t in tags.split(",") if t.strip()]

        catalogo = _cargar_catalogo()

        # ── Paso 1: Inferencia logica ──
        preferencias = {
            "categoria": categoria,
            "nivel": nivel,
            "presupuesto_max": presupuesto_val,
            "tiempo_disponible": tiempo_val,
        }
        recomendados_logicos, altamente_recomendados = inferir_recomendaciones(
            preferencias, catalogo
        )

        # ── Paso 2: Procesamiento funcional ──
        resultados_funcionales = procesar_recomendaciones(
            catalogo, presupuesto=presupuesto_val, tiempo=tiempo_val,
            modalidad=modalidad, tags_usuario=tags_list, top_n=10
        )

        ids_logicos = {c.id for c in recomendados_logicos}
        ids_altos   = {c.id for c in altamente_recomendados}

        combinados = []
        for res in resultados_funcionales:
            curso = res["curso"]
            combinados.append({
                "curso": curso,
                "score": res["score"],
                "es_logico": curso.id in ids_logicos,
                "es_alto": curso.id in ids_altos,
            })

        combinados.sort(key=lambda x: (not x["es_alto"], -x["score"]))

        # ── Paso 3: Cursos relacionados a la profesion ──
        cats_profesion = _categorias_por_profesion(profesion) if profesion else []
        ids_ya_mostrados = {r["curso"].id for r in combinados}

        relacionados_profesion = []
        if cats_profesion:
            for curso in catalogo:
                if curso.categoria in cats_profesion and curso.id not in ids_ya_mostrados:
                    if curso.precio <= presupuesto_val and curso.duracion_horas <= tiempo_val:
                        relacionados_profesion.append({
                            "curso": curso,
                            "score": curso.rating / 5.0,
                            "es_logico": False,
                            "es_alto": curso.rating >= 4.5,
                        })
            relacionados_profesion.sort(key=lambda x: -x["score"])

        # ── Agrupar por categoria para los carruseles ──
        carruseles = {}
        for item in combinados:
            cat = item["curso"].categoria
            if cat not in carruseles:
                carruseles[cat] = []
            carruseles[cat].append(item)

        return render_template(
            "resultado.html",
            recomendaciones=combinados,
            carruseles=carruseles,
            relacionados_profesion=relacionados_profesion,
            cats_profesion=cats_profesion,
            preferencias={
                "categoria": categoria,
                "nivel": nivel,
                "presupuesto": presupuesto_val,
                "tiempo": tiempo_val,
                "modalidad": modalidad,
                "tags": tags_list,
            },
            usuario={
                "nombre": nombre,
                "edad": edad,
                "sexo": sexo,
                "profesion": profesion,
            }
        )

    except Exception as e:
        logger.error(f"Error al procesar recomendacion: {e}")
        flash(f"Ocurrio un error al procesar la solicitud: {str(e)}", "error")
        return redirect(url_for("controller.index"))