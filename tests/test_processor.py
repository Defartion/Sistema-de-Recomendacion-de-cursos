"""
Pruebas unitarias para el modulo processor (paradigma funcional).
"""

import pytest
from models.curso import Curso
from processor.processor import (  # Importa cada función del pipeline funcional por separado para poder testearlas de forma aislada
    filtrar_por_presupuesto,
    filtrar_por_modalidad,
    filtrar_por_tiempo,
    calcular_score,
    obtener_top_n,
    reducir_a_tags_unicos,
    procesar_recomendaciones,  # También se importa el pipeline completo para el test de integración al final
)


@pytest.fixture
def catalogo():  # Fixture compartido: todos los tests que lo pidan como parámetro recibirán esta misma lista limpia
    return [
        Curso(
            id=1, nombre="Curso A", categoria="Programacion", nivel="Principiante",
            duracion_horas=10, precio=50.0, modalidad="Asincrono", plataforma="X",
            rating=4.5, tags=["python", "basico"]   # Rating alto + tags python → ganará el primer lugar en los tests de score
        ),
        Curso(
            id=2, nombre="Curso B", categoria="Datos", nivel="Intermedio",
            duracion_horas=20, precio=100.0, modalidad="Sincrono", plataforma="Y",
            rating=3.5, tags=["sql", "data"]         # Modalidad Sincrono → quedará fuera en filtros de Asincrono
        ),
        Curso(
            id=3, nombre="Curso C", categoria="Diseno", nivel="Avanzado",
            duracion_horas=30, precio=150.0, modalidad="Asincrono", plataforma="Z",
            rating=5.0, tags=["ux", "figma"]         # Precio y duración altos → quedará fuera en filtros estrictos
        ),
        Curso(
            id=4, nombre="Curso D", categoria="Programacion", nivel="Intermedio",
            duracion_horas=15, precio=75.0, modalidad="Asincrono", plataforma="W",
            rating=4.0, tags=["python", "avanzado"]  # Segundo curso con tag python → aparecerá en tests de coincidencia de tags
        ),
    ]


class TestFiltrado:  # Agrupa los tests de las funciones de filtrado individual (una función = un test)
    def test_filtrar_por_presupuesto(self, catalogo):
        resultados = filtrar_por_presupuesto(catalogo, 80.0)
        # Con límite de $80: A ($50) pasa, D ($75) pasa, B ($100) no pasa, C ($150) no pasa
        assert len(resultados) == 2
        assert all(c.precio <= 80.0 for c in resultados)  # Verifica que ningún curso devuelto supere el límite

    def test_filtrar_por_modalidad(self, catalogo):
        resultados = filtrar_por_modalidad(catalogo, "Asincrono")
        # A, C y D son Asincrono; B es Sincrono → B queda fuera
        assert len(resultados) == 3
        assert all(c.modalidad == "Asincrono" for c in resultados)  # Verifica que todos los devueltos sean de la modalidad correcta

    def test_filtrar_por_tiempo(self, catalogo):
        resultados = filtrar_por_tiempo(catalogo, 15)
        # Con límite de 15h: A (10h) pasa, D (15h) pasa, B (20h) no pasa, C (30h) no pasa
        assert len(resultados) == 2
        assert all(c.duracion_horas <= 15 for c in resultados)  # Verifica que todos los devueltos caben en el tiempo disponible


class TestScoreYRanking:  # Agrupa los tests del cálculo de puntuación y ordenamiento
    def test_calcular_score_ordenamiento(self, catalogo):
        scored = calcular_score(catalogo, ["python"])  # Tag "python" coincide con A y D, dándoles ventaja en el componente de tags
        assert len(scored) == 4                        # La función no filtra, todos los cursos reciben un score
        ids_ordenados = [s["curso"].id for s in scored]
        assert ids_ordenados[0] == 1                   # El Curso A debe estar primero: tiene rating 4.5 y coincidencia de tags con "python"

    def test_calcular_score_bonus_nivel(self, catalogo):
        """Los cursos con nivel exacto del usuario obtienen un bonus del 10% en el score."""
        cursos = [c for c in catalogo if c.categoria == "Programacion"]  # Solo A y D para aislar la prueba
        scored_sin_bonus = calcular_score(cursos, [], nivel_usuario="")          # Sin nivel especificado: no hay bonus para nadie
        scored_con_bonus = calcular_score(cursos, [], nivel_usuario="Principiante")  # Con nivel Principiante: A (Principiante) recibirá el bonus

        curso_a     = next(s for s in scored_con_bonus if s["curso"].id == 1)   # Extrae el resultado del Curso A con bonus
        curso_a_sin = next(s for s in scored_sin_bonus if s["curso"].id == 1)   # Extrae el resultado del Curso A sin bonus

        assert curso_a["score"] == pytest.approx(curso_a_sin["score"] * 1.10, rel=1e-5)
        # pytest.approx permite comparar floats con una tolerancia de error relativo de 0.001%
        # porque las operaciones de punto flotante pueden generar diferencias minúsculas como 0.4949999... vs 0.495

    def test_calcular_score_sin_bonus_nivel_diferente(self, catalogo):
        """Los cursos con nivel diferente al del usuario no obtienen bonus."""
        cursos = [c for c in catalogo if c.categoria == "Programacion"]
        scored_diferente = calcular_score(cursos, [], nivel_usuario="Intermedio")  # Usuario Intermedio: D (Intermedio) recibe bonus, A (Principiante) no
        scored_base      = calcular_score(cursos, [], nivel_usuario="")            # Sin nivel: nadie recibe bonus

        curso_a_diferente = next(s for s in scored_diferente if s["curso"].id == 1)  # Curso A cuando usuario es Intermedio
        curso_a_base      = next(s for s in scored_base if s["curso"].id == 1)       # Curso A sin nivel especificado

        assert curso_a_diferente["score"] == pytest.approx(curso_a_base["score"], rel=1e-5)
        # El score de A debe ser idéntico en ambos casos porque A es Principiante, no Intermedio → no recibe bonus

    def test_obtener_top_n(self, catalogo):
        scored = calcular_score(catalogo, ["python"])  # Lista de 4 cursos ordenada por score
        top_2  = obtener_top_n(scored, 2)             # Pide solo los 2 mejores
        assert len(top_2) == 2                         # Verifica que devuelve exactamente 2 cursos
        assert top_2[0]["score"] >= top_2[1]["score"]  # Verifica que el primero tiene score mayor o igual al segundo (orden descendente)


class TestReduccion:  # Agrupa los tests de la función reduce que acumula tags únicos
    def test_reducir_a_tags_unicos(self, catalogo):
        tags = reducir_a_tags_unicos(catalogo)        # Debería juntar todos los tags de los 4 cursos sin repetidos
        assert "python" in tags                        # python aparece en A y D → debe estar una sola vez
        assert "sql" in tags                           # sql aparece solo en B
        assert "ux" in tags                            # ux aparece solo en C
        assert len(tags) == len(set(tags))             # Verifica que no hay duplicados: el largo de la lista debe ser igual al largo del conjunto


class TestCasosLimite:  # Agrupa los tests de situaciones extremas que podrían causar errores si no se manejan correctamente
    def test_lista_vacia(self):  # Este test no necesita el fixture porque trabaja con listas vacías directamente
        assert filtrar_por_presupuesto([], 100.0) == []  # Una lista vacía filtrada debe devolver una lista vacía, no lanzar error
        assert calcular_score([], ["python"])      == []  # calcular_score con lista vacía no debe intentar calcular max_precio ni lanzar ZeroDivisionError
        assert reducir_a_tags_unicos([])           == []  # reduce() con lista vacía devuelve el valor inicial (set vacío) → sorted() lo convierte en []

    def test_ninguna_coincidencia(self, catalogo):
        resultados = filtrar_por_presupuesto(catalogo, 10.0)  # $10 es menor que el precio más bajo del catálogo ($50) → ninguno pasa
        assert resultados == []  # Verifica que devuelve lista vacía en lugar de lanzar error

    def test_todos_cumplen(self, catalogo):
        resultados = filtrar_por_presupuesto(cursos=catalogo, presupuesto_max=200.0)  # $200 supera todos los precios del catálogo → todos pasan
        assert len(resultados) == len(catalogo)  # Verifica que la función no descarta ningún curso cuando todos cumplen la condición


class TestPipelineCompleto:  # Agrupa los tests de integración que prueban el pipeline entero de principio a fin
    def test_procesar_recomendaciones(self, catalogo):
        resultados = procesar_recomendaciones(
            catalogo, presupuesto=80.0, tiempo=15, modalidad="Asincrono",
            tags_usuario=["python"], nivel_usuario="Principiante", top_n=2
            # Con estos filtros: A pasa (Asincrono, $50, 10h, Principiante), D no pasa (15h ≤ 15 sí, pero nivel Intermedio > Principiante no)
        )
        assert len(resultados) <= 2  # Pide máximo 2 resultados; si hay menos candidatos válidos, puede devolver menos
        if resultados:               # Solo verifica los atributos si hubo al menos un resultado (evita IndexError en lista vacía)
            assert resultados[0]["curso"].modalidad     == "Asincrono"  # Verifica que el filtro de modalidad funcionó
            assert resultados[0]["curso"].precio        <= 80.0         # Verifica que el filtro de presupuesto funcionó
            assert resultados[0]["curso"].duracion_horas <= 15          # Verifica que el filtro de tiempo funcionó

    def test_pipeline_vacio_sin_resultados(self, catalogo):
        resultados = procesar_recomendaciones(
            catalogo, presupuesto=0.0, tiempo=0, modalidad="Sincrono",
            tags_usuario=["inexistente"], nivel_usuario="Avanzado", top_n=3
            # presupuesto=0.0 descarta todos los cursos de precio > 0 en el primer filtro
            # tiempo=0 descartaría cualquier curso que sobreviviera (todos duran al menos 1h)
            # El pipeline devuelve [] sin lanzar ningún error
        )
        assert resultados == []  # Verifica que el pipeline maneja correctamente el caso en que ningún curso supera todos los filtros