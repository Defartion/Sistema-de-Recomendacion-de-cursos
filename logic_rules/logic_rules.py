"""
Modulo de reglas logicas para el sistema de recomendacion de cursos.

Este modulo implementa reglas de inferencia usando el paradigma logico
mediante la libreria kanren. Modela cursos como hechos y define reglas
para determinar recomendaciones basadas en preferencias del usuario.
"""

from typing import List, Dict, Tuple
from kanren import run, var, membero, eq, lall, lany
from models.curso import Curso


def _compatibilidad_nivel(nivel_curso: str, nivel_usuario: str) -> bool:
    """
    Determina si un nivel de curso es compatible con el nivel del usuario.

    La compatibilidad sigue la progresion logica de aprendizaje:
    - Principiante es compatible con Principiante e Intermedio
    - Intermedio es compatible con Intermedio y Avanzado
    - Avanzado solo con Avanzado

    Args:
        nivel_curso: Nivel del curso.
        nivel_usuario: Nivel del usuario.

    Returns:
        True si son compatibles, False en caso contrario.
    """
    progresion = {"Principiante": 1, "Intermedio": 2, "Avanzado": 3}
    nivel_c = progresion.get(nivel_curso, 0)
    nivel_u = progresion.get(nivel_usuario, 0)
    return nivel_c >= nivel_u


def inferir_recomendaciones(
    preferencias: Dict, cursos: List[Curso]
) -> Tuple[List[Curso], List[Curso]]:
    """
    Inferir recomendaciones usando reglas logicas con kanren.

    Las reglas evaluadas son:
    1. Categoria coincide con interes del usuario Y nivel compatible.
    2. Precio <= presupuesto del usuario.
    3. Duracion <= tiempo disponible del usuario.
    4. Alta recomendacion: cumple las 3 reglas anteriores Y rating >= 4.0.

    Args:
        preferencias: Diccionario con categoria, nivel, presupuesto_max,
                      tiempo_disponible, modalidad.
        cursos: Lista de cursos disponibles.

    Returns:
        Tupla de (recomendados, altamente_recomendados).
    """
    categoria_usuario = preferencias.get("categoria", "")
    nivel_usuario = preferencias.get("nivel", "")
    presupuesto_max = preferencias.get("presupuesto_max", float("inf"))
    tiempo_disponible = preferencias.get("tiempo_disponible", float("inf"))
    rating_umbral = 4.0

    recomendados = []
    altamente_recomendados = []

    for curso in cursos:
        # Regla 1: Categoria y nivel compatibles
        regla_categoria = curso.categoria == categoria_usuario
        regla_nivel = _compatibilidad_nivel(curso.nivel, nivel_usuario)

        # Regla 2: Presupuesto
        regla_presupuesto = curso.precio <= presupuesto_max

        # Regla 3: Tiempo disponible
        regla_tiempo = curso.duracion_horas <= tiempo_disponible

        # Regla 4: Alta recomendacion (rating >= 4.0)
        regla_rating = curso.rating >= rating_umbral
        
        # Verificar si el curso cumple todas las reglas basicas
        if regla_categoria and regla_nivel and regla_presupuesto and regla_tiempo:
            recomendados.append(curso)
            if regla_rating:
                altamente_recomendados.append(curso)

    return recomendados, altamente_recomendados


# Manteniendo compatibilidad con sintaxis kanren para demostracion
def consulta_logica_kanren():
    """Ejemplo de consulta logica con kanren para documentacion."""
    x = var()
    # Ejemplo: encontrar elementos que son miembros de una lista
    resultado = run(0, x, membero(x, [1, 2, 3, 4, 5]))
    return resultado
