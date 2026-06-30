"""
Pruebas unitarias para el modulo processor (paradigma funcional).
"""

import pytest
from models.curso import Curso
from processor.processor import (
    filtrar_por_presupuesto,
    filtrar_por_modalidad,
    filtrar_por_tiempo,
    calcular_score,
    obtener_top_n,
    reducir_a_tags_unicos,
    procesar_recomendaciones,
)


@pytest.fixture
def catalogo():
    return [
        Curso(
            id=1, nombre="Curso A", categoria="Programacion", nivel="Principiante",
            duracion_horas=10, precio=50.0, modalidad="Asincrono", plataforma="X",
            rating=4.5, tags=["python", "basico"]
        ),
        Curso(
            id=2, nombre="Curso B", categoria="Datos", nivel="Intermedio",
            duracion_horas=20, precio=100.0, modalidad="Sincrono", plataforma="Y",
            rating=3.5, tags=["sql", "data"]
        ),
        Curso(
            id=3, nombre="Curso C", categoria="Diseno", nivel="Avanzado",
            duracion_horas=30, precio=150.0, modalidad="Asincrono", plataforma="Z",
            rating=5.0, tags=["ux", "figma"]
        ),
        Curso(
            id=4, nombre="Curso D", categoria="Programacion", nivel="Intermedio",
            duracion_horas=15, precio=75.0, modalidad="Asincrono", plataforma="W",
            rating=4.0, tags=["python", "avanzado"]
        ),
    ]


class TestFiltrado:
    def test_filtrar_por_presupuesto(self, catalogo):
        resultados = filtrar_por_presupuesto(catalogo, 80.0)
        assert len(resultados) == 2
        assert all(c.precio <= 80.0 for c in resultados)

    def test_filtrar_por_modalidad(self, catalogo):
        resultados = filtrar_por_modalidad(catalogo, "Asincrono")
        assert len(resultados) == 3
        assert all(c.modalidad == "Asincrono" for c in resultados)

    def test_filtrar_por_tiempo(self, catalogo):
        resultados = filtrar_por_tiempo(catalogo, 15)
        assert len(resultados) == 2
        assert all(c.duracion_horas <= 15 for c in resultados)


class TestScoreYRanking:
    def test_calcular_score_ordenamiento(self, catalogo):
        scored = calcular_score(catalogo, ["python"])
        assert len(scored) == 4
        ids_ordenados = [s["curso"].id for s in scored]
        assert ids_ordenados[0] == 1

    def test_calcular_score_bonus_nivel(self, catalogo):
        """Los cursos con nivel exacto del usuario obtienen un bonus del 10% en el score."""
        cursos = [c for c in catalogo if c.categoria == "Programacion"]
        scored_sin_bonus = calcular_score(cursos, [], nivel_usuario="")
        scored_con_bonus = calcular_score(cursos, [], nivel_usuario="Principiante")
        # Curso A (id=1) es Principiante
        curso_a = next(s for s in scored_con_bonus if s["curso"].id == 1)
        curso_a_sin = next(s for s in scored_sin_bonus if s["curso"].id == 1)
        assert curso_a["score"] == pytest.approx(curso_a_sin["score"] * 1.10, rel=1e-5)

    def test_calcular_score_sin_bonus_nivel_diferente(self, catalogo):
        """Los cursos con nivel diferente al del usuario no obtienen bonus."""
        cursos = [c for c in catalogo if c.categoria == "Programacion"]
        scored_diferente = calcular_score(cursos, [], nivel_usuario="Intermedio")
        scored_base = calcular_score(cursos, [], nivel_usuario="")
        # Curso A (id=1) es Principiante, no deberia tener bonus cuando usuario es Intermedio
        curso_a_diferente = next(s for s in scored_diferente if s["curso"].id == 1)
        curso_a_base = next(s for s in scored_base if s["curso"].id == 1)
        # Debe ser el mismo score (sin bonus)
        assert curso_a_diferente["score"] == pytest.approx(curso_a_base["score"], rel=1e-5)

    def test_obtener_top_n(self, catalogo):
        scored = calcular_score(catalogo, ["python"])
        top_2 = obtener_top_n(scored, 2)
        assert len(top_2) == 2
        assert top_2[0]["score"] >= top_2[1]["score"]


class TestReduccion:
    def test_reducir_a_tags_unicos(self, catalogo):
        tags = reducir_a_tags_unicos(catalogo)
        assert "python" in tags
        assert "sql" in tags
        assert "ux" in tags
        assert len(tags) == len(set(tags))


class TestCasosLimite:
    def test_lista_vacia(self):
        assert filtrar_por_presupuesto([], 100.0) == []
        assert calcular_score([], ["python"]) == []
        assert reducir_a_tags_unicos([]) == []

    def test_ninguna_coincidencia(self, catalogo):
        resultados = filtrar_por_presupuesto(catalogo, 10.0)
        assert resultados == []

    def test_todos_cumplen(self, catalogo):
        resultados = filtrar_por_presupuesto(cursos=catalogo, presupuesto_max=200.0)
        assert len(resultados) == len(catalogo)


class TestPipelineCompleto:
    def test_procesar_recomendaciones(self, catalogo):
        resultados = procesar_recomendaciones(
            catalogo, presupuesto=80.0, tiempo=15, modalidad="Asincrono",
            tags_usuario=["python"], nivel_usuario="Principiante", top_n=2
        )
        assert len(resultados) <= 2
        if resultados:
            assert resultados[0]["curso"].modalidad == "Asincrono"
            assert resultados[0]["curso"].precio <= 80.0
            assert resultados[0]["curso"].duracion_horas <= 15

    def test_pipeline_vacio_sin_resultados(self, catalogo):
        resultados = procesar_recomendaciones(
            catalogo, presupuesto=0.0, tiempo=0, modalidad="Sincrono",
            tags_usuario=["inexistente"], nivel_usuario="Avanzado", top_n=3
        )
        assert resultados == []