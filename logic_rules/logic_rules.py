"""
Modulo de reglas logicas para el sistema de recomendacion de cursos.

Este modulo implementa reglas de inferencia usando el paradigma logico
mediante la libreria kanren. Modela cursos como hechos (facts) y define
reglas declarativas para determinar recomendaciones basadas en las
preferencias del usuario.
"""

from typing import List, Dict, Tuple
from kanren import run, var, Relation, facts as kanren_facts
from models.curso import Curso

# Mapeo nivel -> ordinal para la regla de compatibilidad
_NIVEL_ORD = {"Principiante": 1, "Intermedio": 2, "Avanzado": 3}


def _compatibilidad_nivel(nivel_curso: str, nivel_usuario: str) -> bool:
    """Determina si un nivel de curso es compatible con el nivel del usuario."""
    return _NIVEL_ORD.get(nivel_curso, 0) >= _NIVEL_ORD.get(nivel_usuario, 0)


def _construir_relaciones(cursos: List[Curso]) -> Tuple[Relation, Relation, Relation, Relation, Relation]:
    """
    Construye nuevas relaciones de kanren para los cursos dados.

    Cada invocacion retorna relaciones frescas, evitando la acumulacion
    de hechos entre ejecuciones de test.
    """
    curso_categoria = Relation()
    curso_nivel = Relation()
    curso_precio = Relation()
    curso_duracion = Relation()
    curso_rating = Relation()

    for c in cursos:
        kanren_facts(curso_categoria, (c.id, c.categoria))
        kanren_facts(curso_nivel,     (c.id, c.nivel))
        kanren_facts(curso_precio,    (c.id, c.precio))
        kanren_facts(curso_duracion,  (c.id, c.duracion_horas))
        kanren_facts(curso_rating,    (c.id, c.rating))

    return curso_categoria, curso_nivel, curso_precio, curso_duracion, curso_rating


def inferir_recomendaciones(
    preferencias: Dict, cursos: List[Curso]
) -> Tuple[List[Curso], List[Curso]]:
    """
    Inferir recomendaciones usando reglas logicas con kanren.

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

    # 1. Construir relaciones frescas con kanren
    _curso_categoria, _curso_nivel, _curso_precio, _curso_duracion, _curso_rating = _construir_relaciones(cursos)

    # 2. Variables logicas
    id_curso = var()
    nivel_c = var()

    # 3. Consulta logica declarativa con kanren: categoria + nivel
    ids_categoria = run(
        0, id_curso,
        _curso_categoria(id_curso, categoria_usuario),
        _curso_nivel(id_curso, nivel_c),
    )

    # 4. Filtrar en Python las restricciones numericas y de compatibilidad
    ids_filtrados = []
    ids_altos = []
    cursos_por_id = {c.id: c for c in cursos}

    for cid in ids_categoria:
        if cid not in cursos_por_id:
            continue
        curso = cursos_por_id[cid]

        # Reglas 1: Compatibilidad de nivel
        if not _compatibilidad_nivel(curso.nivel, nivel_usuario):
            continue
        # Regla 2: Presupuesto
        if curso.precio > presupuesto_max:
            continue
        # Regla 3: Tiempo
        if curso.duracion_horas > tiempo_disponible:
            continue

        ids_filtrados.append(cid)
        # Regla 4: Alta recomendacion
        if curso.rating >= rating_umbral:
            ids_altos.append(cid)

    recomendados = [cursos_por_id[cid] for cid in ids_filtrados]
    altamente_recomendados = [cursos_por_id[cid] for cid in ids_altos]
    return recomendados, altamente_recomendados
