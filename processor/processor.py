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


def calcular_score(cursos: List[Curso], tags_usuario: List[str]) -> List[dict]:
    """
    Calcula un puntaje de recomendación para cada curso.

    El score pondera:
    - rating del curso (0-5)
    - porcentaje de coincidencia de tags (0-1)
    - cercanía al presupuesto máximo (inverse, 0-1)

    Args:
        cursos: Lista de cursos a evaluar.
        tags_usuario: Tags de interés del usuario para calcular coincidencia.

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
            score_precio = 1.0  # Si todos son gratis, precio no penaliza
        else:
            score_precio = 1.0 - (curso.precio / (max_precio * 2))

        return {
            "curso": curso,
            "score": (score_rating * 0.5) + (score_tags * 0.3) + (max(0, score_precio) * 0.2),
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
    top_n: int = 5,
) -> List[dict]:
    """
    Pipeline completo de procesamiento funcional de recomendaciones.

    Aplica secuencialmente filtros por presupuesto, modalidad y tiempo,
    luego calcula score y retorna el top N.

    Args:
        cursos: Catálogo completo de cursos.
        presupuesto: Presupuesto máximo del usuario.
        tiempo: Horas disponibles del usuario.
        modalidad: Modalidad preferida (Síncrono / Asíncrono).
        tags_usuario: Tags de interés del usuario.
        top_n: Cantidad máxima de resultados a retornar.

    Returns:
        Lista de diccionarios con 'curso' y 'score'.
    """
    cursos_filtrados = filtrar_por_presupuesto(cursos, presupuesto)
    cursos_filtrados = filtrar_por_modalidad(cursos_filtrados, modalidad)
    cursos_filtrados = filtrar_por_tiempo(cursos_filtrados, tiempo)

    scored = calcular_score(cursos_filtrados, tags_usuario)
    return obtener_top_n(scored, top_n)
