"""
Modulo controlador (paradigma imperativo/OO).
"""

import json
import logging
import os
import traceback
from typing import List

from flask import Blueprint, render_template, request, flash, redirect, url_for, session

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
    # Retornar copia para evitar mutación del catálogo cached
    return list(_catalogo_cursos)


# Load profession categories from external JSON file
PROFESIONES_JSON = os.path.join(BASE_DIR, "data", "profesiones.json")


def _cargar_profesiones() -> dict:
    """Load profession categories from JSON file."""
    if os.path.exists(PROFESIONES_JSON):
        with open(PROFESIONES_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _categorias_por_profesion(profesion: str) -> List[str]:
    profesion_lower = profesion.lower()
    profesion_map = _cargar_profesiones()
    categorias = []
    for keyword, cats in profesion_map.items():
        if keyword in profesion_lower:
            for cat in cats:
                if cat not in categorias:
                    categorias.append(cat)
    return categorias


@controller_bp.route("/")
def index():
    return render_template("index.html")


@controller_bp.route("/recomendar", methods=["POST"])
def recomendar():
    try:
        # Datos del onboarding
        nombre    = request.form.get("nombre", "").strip()
        edad      = request.form.get("edad", "").strip()
        sexo      = request.form.get("sexo", "").strip()
        profesion = request.form.get("profesion", "").strip()

        # Preferencias
        categoria  = request.form.get("categoria", "").strip()
        nivel      = request.form.get("nivel", "").strip()
        presupuesto = request.form.get("presupuesto", "0")
        tiempo     = request.form.get("tiempo", "0")
        modalidad  = request.form.get("modalidad", "").strip()
        tags       = request.form.get("tags", "").strip()

        # Mapear valores de display (UI) a valores de datos (JSON)
        MODALIDAD_MAP = {"A mi ritmo": "Asincrono", "En vivo": "Sincrono",
                         "Asincrona": "Asincrono", "Sincro": "Sincrono"}
        modalidad_raw = modalidad
        modalidad = MODALIDAD_MAP.get(modalidad, modalidad)

        try:
            presupuesto_val = float(presupuesto) if presupuesto else 0.0
            tiempo_val = int(float(tiempo)) if tiempo else 0
        except ValueError:
            flash("Los valores de presupuesto y tiempo deben ser numericos.", "error")
            return redirect(url_for("controller.index"))

        if not all([nombre, nivel, tiempo_val]):
            flash("Por favor completa todos los campos obligatorios.", "error")
            return redirect(url_for("controller.index"))

        if edad:
            try:
                edad_num = int(edad)
                if edad_num < 10 or edad_num > 100:
                    flash("La edad debe estar entre 10 y 100 años.", "error")
                    return redirect(url_for("controller.index"))
            except ValueError:
                flash("La edad debe ser un número entero válido.", "error")
                return redirect(url_for("controller.index"))

        if presupuesto_val < 0 or tiempo_val <= 0:
            flash("El presupuesto debe ser positivo y el tiempo mayor a 0.", "error")
            return redirect(url_for("controller.index"))

        # validador de solo gratuitos
        solo_gratuitos = request.form.get("solo_gratuitos", "")
        if solo_gratuitos:
            presupuesto_val = 0.0

        tags_list = [t.strip() for t in tags.split(",") if t.strip()]
        catalogo = _cargar_catalogo()

        # ── Altamente recomendados: cursos que cumplen todos los criterios ──
        preferencias = {
            "categoria": categoria,
            "nivel": nivel,
            "presupuesto_max": presupuesto_val,
            "tiempo_disponible": tiempo_val,
        }
        recomendados_logicos, altamente_recomendados = inferir_recomendaciones(
            preferencias, catalogo
        )

        resultados_funcionales = procesar_recomendaciones(
            catalogo, presupuesto=presupuesto_val, tiempo=tiempo_val,
            modalidad=modalidad, tags_usuario=tags_list, nivel_usuario=nivel, top_n=50
        )

        ids_logicos = {c.id for c in recomendados_logicos}
        ids_altos   = {c.id for c in altamente_recomendados}

        recomendaciones = []
        for res in resultados_funcionales:
            curso = res["curso"]
            recomendaciones.append({
                "curso": curso,
                "score": res["score"],
                "es_logico": curso.id in ids_logicos,
                "es_alto": curso.id in ids_altos,
            })

        recomendaciones.sort(key=lambda x: (not x["es_alto"], -x["score"]))
        mejor_valorados = [
            {"curso": c, "score": c.rating / 5.0, "es_logico": False, "es_alto": True}
            for c in catalogo if c.rating >= 4.7
        ]
        mejor_valorados.sort(key=lambda x: -x["curso"].rating)
        

        # ── Carruseles por categoria: TODOS los cursos del catalogo agrupados ──
        categorias_orden = ["Programacion", "Datos", "Diseno", "Marketing", "Negocios", "Idiomas"]
        carruseles = {}
        for cat in categorias_orden:
            cursos_cat = [
                {"curso": c, "score": c.rating / 5.0, "es_logico": False, "es_alto": c.rating >= 4.5}
                for c in catalogo if c.categoria == cat
            ]
            cursos_cat.sort(key=lambda x: -x["curso"].rating)
            if cursos_cat:
                carruseles[cat] = cursos_cat

        # ── Relacionados a la profesion ──
        cats_profesion = _categorias_por_profesion(profesion) if profesion else []
        ids_recomendados = {r["curso"].id for r in recomendaciones}

        relacionados_profesion = []
        if cats_profesion:
            for curso in catalogo:
                if curso.categoria in cats_profesion and curso.id not in ids_recomendados:
                    relacionados_profesion.append({
                        "curso": curso,
                        "score": curso.rating / 5.0,
                        "es_logico": False,
                        "es_alto": curso.rating >= 4.5,
                    })
            relacionados_profesion.sort(key=lambda x: -x["curso"].rating)

        # Guardar busqueda en sesion para recuperar contexto despues
        session["ultima_busqueda"] = {
            "nombre": nombre,
            "edad": edad,
            "sexo": sexo,
            "profesion": profesion,
            "categoria": categoria,
            "nivel": nivel,
            "presupuesto": presupuesto_val,
            "tiempo": tiempo_val,
            "modalidad": modalidad_raw,
            "tags": tags_list,
        }
        
        # Contadores para la UI
        total_recomendaciones = len(recomendaciones)
        total_relacionados = len(relacionados_profesion)
        total_mejor_valorados = len(mejor_valorados)

        return render_template(
            "resultado.html",
            recomendaciones=recomendaciones,
            mejor_valorados=mejor_valorados,
            carruseles=carruseles,
            relacionados_profesion=relacionados_profesion,
            cats_profesion=cats_profesion,
            total_recomendaciones=total_recomendaciones,
            total_relacionados=total_relacionados,
            total_mejor_valorados=total_mejor_valorados,
            preferencias={
                "categoria": categoria,
                "nivel": nivel,
                "presupuesto": presupuesto_val,
                "tiempo": tiempo_val,
                "modalidad": modalidad_raw,
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
        logger.error(f"Error al procesar recomendacion: {e}\n{traceback.format_exc()}")
        flash("Ocurrio un error al procesar la solicitud. Por favor intenta de nuevo.", "error")
        return redirect(url_for("controller.index"))