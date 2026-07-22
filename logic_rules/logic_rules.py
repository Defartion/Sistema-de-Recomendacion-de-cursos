"""
Modulo de reglas logicas para el sistema de recomendacion de cursos.

Este modulo implementa reglas de inferencia usando el paradigma logico
mediante la libreria kanren. Modela cursos como hechos (facts) y define
reglas declarativas para determinar recomendaciones basadas en las
preferencias del usuario.
"""

from typing import List, Dict, Tuple  # List y Dict para tipado de parámetros; Tuple porque la función principal retorna dos listas empaquetadas
from kanren import run, var, Relation, facts as kanren_facts
# run     → ejecuta una consulta lógica y devuelve los resultados que satisfacen todas las condiciones
# var     → crea una variable lógica sin valor asignado, kanren la resolverá durante la consulta
# Relation→ crea una relación vacía (como una tabla) donde se registrarán hechos
# kanren_facts → registra hechos (filas) dentro de una Relation
from models.curso import Curso  # Importa la clase Curso para tipar las listas que recibe y retorna este módulo

# Mapeo nivel -> ordinal para la regla de compatibilidad
# Se define a nivel de módulo porque es una constante compartida con processor.py
# Ambos módulos usan la misma jerarquía: Principiante=1, Intermedio=2, Avanzado=3
_NIVEL_ORD = {"Principiante": 1, "Intermedio": 2, "Avanzado": 3}


def _compatibilidad_nivel(nivel_curso: str, nivel_usuario: str) -> bool:
    """Determina si un nivel de curso es compatible con el nivel del usuario.
    Un curso es compatible si su nivel es <= al nivel del usuario
    (un principiante no debería ver cursos avanzados)."""
    # .get() con valor por defecto evita KeyError si llega un nivel desconocido
    # nivel_curso desconocido → 0 (por debajo de todo, siempre compatible)
    # nivel_usuario desconocido → 3 (acepta cualquier nivel de curso)
    return _NIVEL_ORD.get(nivel_curso, 0) <= _NIVEL_ORD.get(nivel_usuario, 3)


def _construir_relaciones(cursos: List[Curso]) -> Tuple[Relation, Relation, Relation, Relation, Relation]:
    """
    Construye nuevas relaciones de kanren para los cursos dados.

    Cada invocacion retorna relaciones frescas, evitando la acumulacion
    de hechos entre ejecuciones de test.
    """
    # Se crean cinco Relation vacías, una por cada atributo que usarán las reglas lógicas
    # Cada Relation es como una tabla de dos columnas: (id_curso, valor_del_atributo)
    curso_categoria = Relation()  # Tabla: qué categoría tiene cada curso
    curso_nivel     = Relation()  # Tabla: qué nivel tiene cada curso
    curso_precio    = Relation()  # Tabla: cuánto cuesta cada curso
    curso_duracion  = Relation()  # Tabla: cuántas horas dura cada curso
    curso_rating    = Relation()  # Tabla: qué calificación tiene cada curso

    for c in cursos:  # Recorre el catálogo completo y registra cada curso como un conjunto de hechos en las cinco relaciones
        kanren_facts(curso_categoria, (c.id, c.categoria))    # Hecho: "el curso con este id pertenece a esta categoría"
        kanren_facts(curso_nivel,     (c.id, c.nivel))        # Hecho: "el curso con este id tiene este nivel"
        kanren_facts(curso_precio,    (c.id, c.precio))       # Hecho: "el curso con este id cuesta este precio"
        kanren_facts(curso_duracion,  (c.id, c.duracion_horas))  # Hecho: "el curso con este id dura estas horas"
        kanren_facts(curso_rating,    (c.id, c.rating))       # Hecho: "el curso con este id tiene esta calificación"

    # IMPORTANTE: se crean relaciones nuevas en cada llamada (no se reusan las anteriores)
    # kanren acumula hechos globalmente; si se reutilizaran las mismas relaciones entre llamadas,
    # los hechos de una búsqueda contaminarían las siguientes y los tests fallarían
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
    # ── Extraer preferencias del usuario ──
    categoria_usuario = preferencias.get("categoria", "")          # Categoría que eligió el usuario; cadena vacía si no eligió ninguna
    nivel_usuario     = preferencias.get("nivel", "")              # Nivel del usuario; cadena vacía si no se especificó
    presupuesto_max   = preferencias.get("presupuesto_max", float("inf"))   # Presupuesto máximo; float("inf") significa sin límite si no se especificó
    tiempo_disponible = preferencias.get("tiempo_disponible", float("inf")) # Horas disponibles; float("inf") significa sin límite si no se especificó
    rating_umbral     = 4.0  # Calificación mínima para que un curso sea considerado "altamente recomendado"

    # ── Paso 1: Construir relaciones frescas con kanren ──
    # Se desestructura la tupla que retorna _construir_relaciones en cinco variables,
    # con guion bajo al inicio para indicar que son de uso interno en esta función
    _curso_categoria, _curso_nivel, _curso_precio, _curso_duracion, _curso_rating = _construir_relaciones(cursos)

    # ── Paso 2: Declarar variables lógicas ──
    id_curso = var()  # Variable lógica que kanren resolverá con los ids de cursos que cumplan las condiciones
    nivel_c  = var()  # Variable lógica auxiliar para que kanren pueda unificar el nivel de cada curso sin restringirlo a un valor fijo

    # ── Paso 3: Consulta lógica declarativa con kanren ──
    # run(0, ...) significa "dame TODOS los resultados posibles" (0 = sin límite)
    # Se le pide a kanren: "encuentra todos los id_curso tales que..."
    ids_categoria = run(
        0, id_curso,
        _curso_categoria(id_curso, categoria_usuario),  # ...pertenezcan a la categoría del usuario
        _curso_nivel(id_curso, nivel_c),                # ...y tengan algún nivel registrado (nivel_c actúa como comodín)
    )
    # kanren resuelve esto por unificación: prueba todas las combinaciones de hechos
    # hasta encontrar las que satisfacen ambas condiciones simultáneamente
    # El resultado es una tupla de ids de cursos que pasaron la consulta declarativa

    # ── Paso 4: Filtrar restricciones numéricas en Python puro ──
    # kanren no maneja comparaciones numéricas (>, <, <=) de forma nativa,
    # por eso las restricciones de presupuesto, tiempo y nivel se aplican aquí en Python
    ids_filtrados = []  # Acumulará los ids de cursos que pasan TODAS las reglas
    ids_altos     = []  # Acumulará los ids de cursos que además tienen rating >= 4.0
    cursos_por_id = {c.id: c for c in cursos}  # Diccionario id→Curso para acceder en O(1) sin recorrer la lista completa cada vez

    for cid in ids_categoria:  # Recorre solo los ids que kanren encontró válidos por categoría y nivel
        if cid not in cursos_por_id:  # Verificación defensiva: descarta ids que por alguna razón no estén en el catálogo
            continue

        curso = cursos_por_id[cid]  # Obtiene el objeto Curso completo a partir de su id

        # Regla 1: Compatibilidad de nivel
        # Aunque kanren ya filtró por categoría, el nivel aún no fue restringido (nivel_c era comodín)
        # Aquí se aplica la restricción real: el curso no puede ser más difícil que el usuario
        if not _compatibilidad_nivel(curso.nivel, nivel_usuario):
            continue  # Descarta el curso y pasa al siguiente

        # Regla 2: Presupuesto
        if curso.precio > presupuesto_max:  # El precio del curso supera lo que el usuario puede pagar
            continue

        # Regla 3: Tiempo
        if curso.duracion_horas > tiempo_disponible:  # El curso dura más horas de las que el usuario tiene disponibles
            continue

        ids_filtrados.append(cid)  # El curso pasó las tres reglas numéricas; se agrega a la lista de recomendados

        # Regla 4: Alta recomendación
        if curso.rating >= rating_umbral:  # Si además tiene calificación >= 4.0, se marca como altamente recomendado
            ids_altos.append(cid)

    # ── Construir listas de retorno ──
    recomendados            = [cursos_por_id[cid] for cid in ids_filtrados]  # Convierte ids a objetos Curso completos
    altamente_recomendados  = [cursos_por_id[cid] for cid in ids_altos]      # Lo mismo para los de alta calificación
    return recomendados, altamente_recomendados  # El controller recibirá ambas listas y las usará para construir los flags es_logico y es_alto