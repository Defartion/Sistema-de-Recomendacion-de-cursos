"""
Módulo de procesamiento funcional para el sistema de recomendación de cursos.

Este módulo implementa operaciones de filtrado, transformación y ranking
utilizando exclusivamente funciones puras del paradigma funcional:
map, filter, reduce y expresiones lambda.

Todas las funciones son determinísticas y libres de efectos secundarios.
"""

from functools import reduce  # reduce() acumula una lista en un único valor aplicando una función de a dos elementos; se usa al final para juntar todos los tags en un solo conjunto
from typing import List  # Permite declarar que un parámetro o retorno es una lista de cierto tipo

from models.curso import Curso  # Importa la clase Curso para que las funciones puedan recibir y retornar objetos de ese tipo


def filtrar_por_presupuesto(
    cursos: List[Curso], presupuesto_max: float) -> List[Curso]:
    """
    Filtra cursos cuyo precio sea menor o igual al presupuesto máximo.
    """
    # filter() recorre la lista y conserva solo los elementos donde la lambda devuelve True
    # La lambda recibe cada curso (c) y evalúa si su precio cabe dentro del presupuesto del usuario
    return list(filter(lambda c: c.precio <= presupuesto_max, cursos))


def filtrar_por_modalidad(
    cursos: List[Curso], modalidad: str) -> List[Curso]:
    """
    Filtra cursos por la modalidad de entrega especificada.
    Si la modalidad está vacía, devuelve todos los cursos sin filtrar.
    """
    if not modalidad:  # Si el usuario no eligió ninguna modalidad, no se aplica este filtro y se devuelven todos los cursos
        return cursos
    # .lower() en ambos lados hace la comparación insensible a mayúsculas/minúsculas
    # evita que "Asincrono" y "asincrono" sean tratados como valores distintos
    return list(filter(lambda c: c.modalidad.lower() == modalidad.lower(), cursos))


def filtrar_por_tiempo(
    cursos: List[Curso], tiempo_max: int) -> List[Curso]:
    """
    Filtra cursos cuya duración sea menor o igual al tiempo disponible.
    """
    # Conserva solo los cursos que el usuario puede completar
    # dentro de las horas que indicó tener disponibles
    return list(filter(lambda c: c.duracion_horas <= tiempo_max, cursos))


# ── Nivel por compatibilidad (misma regla que logic_rules.py) ──
_NIVEL_ORD = {"Principiante": 1, "Intermedio": 2, "Avanzado": 3}
# Diccionario que convierte el nivel textual a un número para poder comparar jerarquías
# Se define a nivel de módulo (fuera de funciones) porque es una constante compartida


def _compatibilidad_nivel(nivel_curso: str, nivel_usuario: str) -> bool:
    # Convierte ambos niveles a número y verifica que el curso no sea más difícil que el usuario
    # Si el nivel del curso no está en el diccionario, se asigna 0 (por debajo de todo)
    # Si el nivel del usuario no está en el diccionario, se asigna 3 (acepta cualquier nivel)
    return _NIVEL_ORD.get(nivel_curso, 0) <= _NIVEL_ORD.get(nivel_usuario, 3)


def filtrar_por_nivel(
    cursos: List[Curso], nivel_usuario: str
) -> List[Curso]:
    """
    Filtra cursos cuyo nivel sea menor o igual al nivel del usuario.
    Un usuario Avanzado puede ver cursos de nivel Intermedio y Principiante también.
    """
    if not nivel_usuario:  # Si el usuario no especificó nivel, no se restringe por este criterio
        return cursos
    # _compatibilidad_nivel devuelve True si el curso es apto para el nivel del usuario
    return list(filter(lambda c: _compatibilidad_nivel(c.nivel, nivel_usuario), cursos))


def calcular_score(cursos: List[Curso], tags_usuario: List[str], nivel_usuario: str = "") -> List[dict]:
    """
    Calcula un puntaje de recomendación para cada curso.

    El score pondera:
    - rating del curso (peso 50%)
    - porcentaje de coincidencia de tags (peso 30%)
    - cercanía al presupuesto máximo (peso 20%)
    - bonus si el nivel coincide exactamente con el del usuario
    """
    def _score_curso(curso: Curso) -> dict:  # Función interna pura que calcula el score de un curso individual; se define aquí para poder acceder a tags_usuario y nivel_usuario sin pasarlos como parámetros
        
        score_rating = curso.rating / 5.0  # Normaliza el rating a escala 0.0–1.0 dividiendo entre el máximo posible (5.0)

        if tags_usuario:  # Solo calcula coincidencia de tags si el usuario indicó alguno
            coincidencias = sum(
                1 for t in tags_usuario if t.lower() in [tag.lower() for tag in curso.tags]
                # Cuenta cuántos tags del usuario aparecen en los tags del curso (comparación sin mayúsculas)
            )
            score_tags = coincidencias / len(tags_usuario)  # Proporción de tags que coinciden: 1.0 si todos coinciden, 0.0 si ninguno
        else:
            score_tags = 0.0  # Si el usuario no indicó tags, este componente no aporta al score

        max_precio = max(c.precio for c in cursos) if cursos else 1.0  # Busca el precio más alto del catálogo filtrado para poder normalizar; si la lista está vacía usa 1.0 para evitar división por cero
        if max_precio == 0:
            score_precio = 1.0  # Si todos los cursos son gratuitos, todos tienen el máximo score de precio
        else:
            score_precio = 1.0 - (curso.precio / (max_precio * 2))
            # Cursos más baratos obtienen score_precio más cercano a 1.0
            # Se divide entre max_precio * 2 para que incluso el curso más caro obtenga un score positivo (0.5) en lugar de 0

        # Fórmula final ponderada: rating aporta 50%, tags 30%, precio 20%
        score_total = (score_rating * 0.5) + (score_tags * 0.3) + (max(0, score_precio) * 0.2)
        # max(0, score_precio) evita que un precio muy alto genere un score negativo que penalice el total

        # Bonus del 10% si el nivel coincide exactamente
        if nivel_usuario and curso.nivel == nivel_usuario:  # Si el curso es del nivel exacto que pidió el usuario, se premia con un 10% adicional
            score_total *= 1.10

        return {
            "curso": curso,    # El objeto Curso completo para que el controller pueda acceder a todos sus datos
            "score": score_total,  # El puntaje calculado que determinará el orden final de recomendaciones
        }

    cursos_con_score = list(map(_score_curso, cursos))
    # map() aplica _score_curso a cada curso de la lista y devuelve un iterador; list() lo convierte en lista
    return sorted(cursos_con_score, key=lambda x: x["score"], reverse=True)
    # sorted() ordena la lista de mayor a menor score; reverse=True invierte el orden natural (ascendente) a descendente


def obtener_top_n(cursos_scored: List[dict], n: int) -> List[dict]:
    """
    Retorna los N cursos con mayor score.
    """
    return cursos_scored[:n]  # Slicing de Python: toma los primeros N elementos de la lista ya ordenada; si hay menos de N cursos, devuelve todos sin error


def reducir_a_tags_unicos(cursos: List[Curso]) -> List[str]:
    """
    Extrae y deduplica todos los tags presentes en una lista de cursos.
    Usa reduce para acumular un conjunto de tags únicos.
    """
    return sorted(
        reduce(lambda acc, c: acc | set(c.tags), cursos, set())
        # reduce() parte de un conjunto vacío (set()) y en cada paso une (|) los tags del curso actual con los acumulados
        # Al final acc contiene todos los tags de todos los cursos sin repetidos
        # sorted() convierte el conjunto a lista ordenada alfabéticamente
    )


def procesar_recomendaciones(
    cursos: List[Curso],
    presupuesto: float,
    tiempo: int,
    modalidad: str,
    tags_usuario: List[str],
    nivel_usuario: str,
    top_n: int = 5,  # Si no se especifica cuántos resultados devolver, el valor por defecto es 5; el controller lo llama con top_n=50
) -> List[dict]:
    """
    Pipeline completo de procesamiento funcional de recomendaciones.

    Aplica secuencialmente filtros por presupuesto, modalidad, tiempo y nivel,
    luego calcula score y retorna el top N.
    """
    # ── Pipeline secuencial de filtros ──
    # Cada función recibe la lista que devolvió la anterior, reduciendo el catálogo progresivamente
    # La lista original nunca se modifica: cada función devuelve una lista nueva
    cursos_filtrados = filtrar_por_presupuesto(cursos, presupuesto)       # Paso 1: descarta cursos fuera del presupuesto
    cursos_filtrados = filtrar_por_modalidad(cursos_filtrados, modalidad)  # Paso 2: descarta cursos de modalidad incorrecta
    cursos_filtrados = filtrar_por_tiempo(cursos_filtrados, tiempo)        # Paso 3: descarta cursos que duran más de lo disponible
    cursos_modern    = filtrar_por_nivel(cursos_filtrados, nivel_usuario)  # Paso 4: descarta cursos de nivel incompatible con el usuario

    scored = calcular_score(cursos_modern, tags_usuario, nivel_usuario)    # Paso 5: calcula el score de cada curso que sobrevivió los filtros y los ordena
    return obtener_top_n(scored, top_n)                                    # Paso 6: devuelve solo los N mejores al controller