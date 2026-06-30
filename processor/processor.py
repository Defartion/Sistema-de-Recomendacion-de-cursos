"""
Módulo de procesamiento funcional para el sistema de recomendación de cursos.

Este módulo implementa operaciones de filtrado, transformación y ranking
utilizando exclusivamente funciones puras del paradigma funcional:
map, filter, reduce y expresiones lambda.

Todas las funciones son determinísticas y libres de efectos secundarios.
"""

from functools import reduce
from typing import List

from models.curso import Curso


def filtrar_por_presupuesto(
    cursos: List[Curso], presupuesto_max: float
) -> List[Curso]:
    """
    Filtra cursos cuyo precio sea menor o igual al presupuesto máximo.

    Args:
        cursos: Lista de cursos a filtrar.
        presupuesto_max: Monto máximo que el usuario puede invertir.

    Returns:
        Lista de cursos que cumplen la condición de presupuesto.
    """
    return list(filter(lambda c: c.precio <= presupuesto_max, cursos))


def filtrar_por_modalidad(
    cursos: List[Curso], modalidad: str
) -> List[Curso]:
    """
    Filtra cursos por la modalidad de entrega especificada.
    Si la modalidad está vacía, devuelve todos los cursos sin filtrar.
    """
    if not modalidad:
        return cursos
    return list(filter(lambda c: c.modalidad.lower() == modalidad.lower(), cursos))


def filtrar_por_tiempo(
    cursos: List[Curso], tiempo_max: int
) -> List[Curso]:
    """
    Filtra cursos cuya duración sea menor o igual al tiempo disponible.

    Args:
        cursos: Lista de cursos a filtrar.
        tiempo_max: Horas máximas disponibles para estudiar.

    Returns:
        Lista de cursos que se ajustan al tiempo disponible.
    """
    return list(filter(lambda c: c.duracion_horas <= tiempo_max, cursos))


# ── Nivel por compatibilidad (misma regla que logic_rules.py) ──
_NIVEL_ORD = {"Principiante": 1, "Intermedio": 2, "Avanzado": 3}


def _compatibilidad_nivel(nivel_curso: str, nivel_usuario: str) -> bool:
    return _NIVEL_ORD.get(nivel_curso, 0) <= _NIVEL_ORD.get(nivel_usuario, 3)


def filtrar_por_nivel(
    cursos: List[Curso], nivel_usuario: str
) -> List[Curso]:
    """
    Filtra cursos cuyo nivel sea menor o igual al nivel del usuario.
    Un usuario Avanzado puede ver cursos de nivel Intermedio y Principiante también.

    Args:
        cursos: Lista de cursos a filtrar.
        nivel_usuario: Nivel del usuario (Principiante/Intermedio/Avanzado).

    Returns:
        Lista de cursos compatibles con el nivel del usuario.
    """
    if not nivel_usuario:
        return cursos
    return list(filter(lambda c: _compatibilidad_nivel(c.nivel, nivel_usuario), cursos))


def calcular_score(cursos: List[Curso], tags_usuario: List[str], nivel_usuario: str = "") -> List[dict]:
    """
    Calcula un puntaje de recomendación para cada curso.

    El score pondera:
    - rating del curso (0-5)
    - porcentaje de coincidencia de tags (0-1)
    - cercanía al presupuesto máximo (inverse, 0-1)
    - bonus si el nivel coincide exactamente con el del usuario

    Args:
        cursos: Lista de cursos a evaluar.
        tags_usuario: Tags de interés del usuario para calcular coincidencia.
        nivel_usuario: Nivel del usuario para dar bonus de coincidencia exacta.

    Returns:
        Lista de diccionarios {'curso': Curso, 'score': float} ordenada
        por score descendente.
    """
    def _score_curso(curso: Curso) -> dict:
        score_rating = curso.rating / 5.0
        if tags_usuario:
            coincidencias = sum(
                1 for t in tags_usuario if t.lower() in [tag.lower() for tag in curso.tags]
            )
            score_tags = coincidencias / len(tags_usuario)
        else:
            score_tags = 0.0

        max_precio = max(c.precio for c in cursos) if cursos else 1.0
        if max_precio == 0:
            score_precio = 1.0
        else:
            score_precio = 1.0 - (curso.precio / (max_precio * 2))
        
        score_total = (score_rating * 0.5) + (score_tags * 0.3) + (max(0, score_precio) * 0.2)
        
        # Bonus del 10% si el nivel coincide exactamente
        if nivel_usuario and curso.nivel == nivel_usuario:
            score_total *= 1.10
        
        return {
            "curso": curso,
            "score": score_total,
        }

    cursos_con_score = list(map(_score_curso, cursos))
    return sorted(cursos_con_score, key=lambda x: x["score"], reverse=True)


def obtener_top_n(cursos_scored: List[dict], n: int) -> List[dict]:
    """
    Retorna los N cursos con mayor score.

    Args:
        cursos_scored: Lista de diccionarios con 'curso' y 'score'.
        n: Cantidad de resultados a retornar.

    Returns:
        Sublista con los N mejores cursos.
    """
    return cursos_scored[:n]


def reducir_a_tags_unicos(cursos: List[Curso]) -> List[str]:
    """
    Extrae y deduplica todos los tags presentes en una lista de cursos.

    Usa reduce para acumular un conjunto de tags únicos.

    Args:
        cursos: Lista de cursos.

    Returns:
        Lista ordenada de tags únicos.
    """
    return sorted(
        reduce(lambda acc, c: acc | set(c.tags), cursos, set())
    )


def procesar_recomendaciones(
    cursos: List[Curso],
    presupuesto: float,
    tiempo: int,
    modalidad: str,
    tags_usuario: List[str],
    nivel_usuario: str,
    top_n: int = 5,
) -> List[dict]:
    """
    Pipeline completo de procesamiento funcional de recomendaciones.

    Aplica secuencialmente filtros por presupuesto, modalidad, tiempo y nivel,
    luego calcula score y retorna el top N.

    Args:
        cursos: Catálogo comple de cursos.
        presupuesto: Presupuesto máximo del usuario.
        tiempo: Horas disponibles del usuario.
        modalidad: Modalidad preferida (Síncrono / Asíncrono).
        tags_usuario: Tags de interés del usuario.
        nivel_usuario: Nivel del usuario (Principiante/Intermedio/Avanzado).
        top_n: Cantidad máxima de resultados a retornar.

    Returns:
        Lista de diccionarios con 'curso' y 'score'.
    """
    cursos_filtrados = filtrar_por_presupuesto(cursos, presupuesto)
    cursos_filtrados = filtrar_por_modalidad(cursos_filtrados, modalidad)
    cursos_filtrados = filtrar_por_tiempo(cursos_filtrados, tiempo)
    cursos_modern = filtrar_por_nivel(cursos_filtrados, nivel_usuario)

    scored = calcular_score(cursos_modern, tags_usuario, nivel_usuario)
    return obtener_top_n(scored, top_n)
