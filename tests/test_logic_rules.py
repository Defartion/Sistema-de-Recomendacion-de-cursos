"""
Pruebas unitarias para el modulo logic_rules (paradigma logico).
"""

import pytest
from models.curso import Curso
from logic_rules.logic_rules import inferir_recomendaciones


@pytest.fixture
def catalogo_prueba():
    """Catalogo de cursos para pruebas logicas."""
    return [
        Curso(id=1, nombre="Curso A", categoria="Programacion", nivel="Principiante",
              duracion_horas=10, precio=50.0, modalidad="Asincrono", plataforma="X",
              rating=4.5, tags=["python"]),
        Curso(id=2, nombre="Curso B", categoria="Programacion", nivel="Intermedio",
              duracion_horas=20, precio=100.0, modalidad="Sincrono", plataforma="Y",
              rating=3.8, tags=["java"]),
        Curso(id=3, nombre="Curso C", categoria="Datos", nivel="Avanzado",
              duracion_horas=15, precio=80.0, modalidad="Asincrono", plataforma="Z",
              rating=4.2, tags=["sql"]),
        Curso(id=4, nombre="Curso D", categoria="Programacion", nivel="Principiante",
              duracion_horas=5, precio=30.0, modalidad="Asincrono", plataforma="W",
              rating=3.9, tags=["python"]),
    ]


class TestReglasLogicas:
    def test_recomendacion_basica(self, catalogo_prueba):
        """Test de recomendacion basica por categoria y nivel."""
        preferencias = {
            "categoria": "Programacion",
            "nivel": "Principiante",
            "presupuesto_max": 200.0,
            "tiempo_disponible": 100,
        }
        recomendados, altos = inferir_recomendaciones(preferencias, catalogo_prueba)
        # Deberia recomendar cursos de Programacion con nivel Principiante o mayor
        assert len(recomendados) == 3  # A, B, D (todos son Programacion con nivel >= Principiante)
        assert all(c.categoria == "Programacion" for c in recomendados)

    def test_filtro_presupuesto(self, catalogo_prueba):
        """Test que filtra por presupuesto."""
        preferencias = {
            "categoria": "Programacion",
            "nivel": "Principiante",
            "presupuesto_max": 60.0,
            "tiempo_disponible": 100,
        }
        recomendados, altos = inferir_recomendaciones(preferencias, catalogo_prueba)
        assert len(recomendados) == 2  # Solo A (50.0) y D (30.0)
        assert all(c.precio <= 60.0 for c in recomendados)

    def test_filtro_tiempo(self, catalogo_prueba):
        """Test que filtra por tiempo disponible."""
        preferencias = {
            "categoria": "Programacion",
            "nivel": "Principiante",
            "presupuesto_max": 200.0,
            "tiempo_disponible": 8,
        }
        recomendados, altos = inferir_recomendaciones(preferencias, catalogo_prueba)
        # Con tiempo=8h solo D (5h) cumple, A (10h) no cumple
        assert len(recomendados) == 1
        assert all(c.duracion_horas <= 8 for c in recomendados)

    def test_alta_recomendacion_rating(self, catalogo_prueba):
        """Test que identifica cursos altamente recomendados (rating >= 4.0)."""
        preferencias = {
            "categoria": "Programacion",
            "nivel": "Principiante",
            "presupuesto_max": 200.0,
            "tiempo_disponible": 100,
        }
        recomendados, altos = inferir_recomendaciones(preferencias, catalogo_prueba)
        # Curso A tiene rating 4.5, D tiene 3.9, B tiene 3.8
        assert len(altos) == 1  # Solo A cumple rating >= 4.0
        assert altos[0].id == 1

    def test_sin_coincidencias(self, catalogo_prueba):
        """Test cuando no hay cursos que cumplan las reglas."""
        preferencias = {
            "categoria": "Marketing",
            "nivel": "Principiante",
            "presupuesto_max": 200.0,
            "tiempo_disponible": 100,
        }
        recomendados, altos = inferir_recomendaciones(preferencias, catalogo_prueba)
        assert recomendados == []
        assert altos == []

    def test_compatibilidad_nivel(self, catalogo_prueba):
        """Test de compatibilidad de nivel entre usuario y curso."""
        preferencias = {
            "categoria": "Programacion",
            "nivel": "Intermedio",  # Usuario intermedio puede ver intermedio y avanzado
            "presupuesto_max": 200.0,
            "tiempo_disponible": 100,
        }
        recomendados, altos = inferir_recomendaciones(preferencias, catalogo_prueba)
        # Usuario intermedio: nivel_c >= nivel_u (2 >= 2)
        # Curso A (Principiante=1) no cumple, B (Intermedio=2) si, D (Principiante=1) no
        assert len(recomendados) == 1  # Solo B
        assert recomendados[0].id == 2
