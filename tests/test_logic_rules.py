"""
Pruebas unitarias para el modulo logic_rules (paradigma logico).
"""

import pytest
from models.curso import Curso  # Importa la clase Curso para poder crear objetos de prueba directamente en los tests
from logic_rules.logic_rules import inferir_recomendaciones  # Importa la función principal del módulo lógico que se va a testear


@pytest.fixture
def catalogo_prueba():  # Fixture compartido: todos los tests de este archivo pueden pedirlo como parámetro y recibirán esta misma lista
    """Catalogo de cursos para pruebas logicas."""
    # Se crea un catálogo reducido y controlado de 4 cursos en lugar de usar los 57 reales
    # Esto permite saber exactamente cuántos resultados esperar en cada test sin depender del JSON externo
    return [
        Curso(id=1, nombre="Curso A", categoria="Programacion", nivel="Principiante",
              duracion_horas=10, precio=50.0, modalidad="Asincrono", plataforma="X",
              rating=4.5, tags=["python"]),   # Programacion · Principiante · 10h · $50 · rating 4.5 → pasará los filtros de rating >= 4.0
        Curso(id=2, nombre="Curso B", categoria="Programacion", nivel="Intermedio",
              duracion_horas=20, precio=100.0, modalidad="Sincrono", plataforma="Y",
              rating=3.8, tags=["java"]),     # Programacion · Intermedio · 20h · $100 · rating 3.8 → no llegará a altamente_recomendados
        Curso(id=3, nombre="Curso C", categoria="Datos", nivel="Avanzado",
              duracion_horas=15, precio=80.0, modalidad="Asincrono", plataforma="Z",
              rating=4.2, tags=["sql"]),      # Datos (distinta categoría) → nunca aparecerá en tests de Programacion
        Curso(id=4, nombre="Curso D", categoria="Programacion", nivel="Principiante",
              duracion_horas=5, precio=30.0, modalidad="Asincrono", plataforma="W",
              rating=3.9, tags=["python"]),   # Programacion · Principiante · 5h · $30 · rating 3.9 → pasa filtros pero no llega a altamente_recomendados
    ]


class TestReglasLogicas:  # Agrupa todos los tests del módulo lógico en una sola clase para organizarlos visualmente
    def test_recomendacion_basica(self, catalogo_prueba):  # catalogo_prueba viene del fixture definido arriba
        """Test de recomendacion basica por categoria y nivel."""
        preferencias = {
            "categoria": "Programacion",
            "nivel": "Principiante",    # Solo puede ver cursos de nivel Principiante (nivel <= 1)
            "presupuesto_max": 200.0,   # Presupuesto amplio para que no elimine ningún curso
            "tiempo_disponible": 100,   # Tiempo amplio para que no elimine ningún curso
        }
        recomendados, altos = inferir_recomendaciones(preferencias, catalogo_prueba)
        # Deberia recomendar cursos de Programacion con nivel Principiante o menor
        assert len(recomendados) == 2  # Solo A (Principiante) y D (Principiante); B queda fuera porque es Intermedio (2 > 1)
        assert all(c.categoria == "Programacion" for c in recomendados)  # Verifica que todos los devueltos sean de la categoría correcta

    def test_filtro_presupuesto(self, catalogo_prueba):
        """Test que filtra por presupuesto."""
        preferencias = {
            "categoria": "Programacion",
            "nivel": "Principiante",
            "presupuesto_max": 60.0,    # Límite de $60: A cuesta $50 (pasa), D cuesta $30 (pasa), B cuesta $100 (no pasa)
            "tiempo_disponible": 100,
        }
        recomendados, altos = inferir_recomendaciones(preferencias, catalogo_prueba)
        assert len(recomendados) == 2  # Solo A ($50) y D ($30) quedan dentro del presupuesto
        assert all(c.precio <= 60.0 for c in recomendados)  # Verifica que ningún curso devuelto supere el límite

    def test_filtro_tiempo(self, catalogo_prueba):
        """Test que filtra por tiempo disponible."""
        preferencias = {
            "categoria": "Programacion",
            "nivel": "Principiante",
            "presupuesto_max": 200.0,
            "tiempo_disponible": 8,     # Solo 8 horas disponibles: D dura 5h (pasa), A dura 10h (no pasa)
        }
        recomendados, altos = inferir_recomendaciones(preferencias, catalogo_prueba)
        # Con tiempo=8h solo D (5h) cumple, A (10h) no cumple
        assert len(recomendados) == 1                              # Solo D pasa el filtro de tiempo
        assert all(c.duracion_horas <= 8 for c in recomendados)   # Verifica que el curso devuelto cabe en el tiempo disponible

    def test_alta_recomendacion_rating(self, catalogo_prueba):
        """Test que identifica cursos altamente recomendados (rating >= 4.0)."""
        preferencias = {
            "categoria": "Programacion",
            "nivel": "Principiante",
            "presupuesto_max": 200.0,
            "tiempo_disponible": 100,
        }
        recomendados, altos = inferir_recomendaciones(preferencias, catalogo_prueba)
        # De los cursos Principiante de Programacion: A tiene 4.5 (pasa), D tiene 3.9 (no pasa)
        # B tiene 3.8 pero ya fue descartado por ser Intermedio, así que ni llega a esta verificación
        assert len(altos) == 1       # Solo el Curso A supera el umbral de rating >= 4.0
        assert altos[0].id == 1      # Verifica que el altamente recomendado sea exactamente el Curso A

    def test_sin_coincidencias(self, catalogo_prueba):
        """Test cuando no hay cursos que cumplan las reglas."""
        preferencias = {
            "categoria": "Marketing",   # No existe ningún curso de Marketing en el catálogo de prueba
            "nivel": "Principiante",
            "presupuesto_max": 200.0,
            "tiempo_disponible": 100,
        }
        recomendados, altos = inferir_recomendaciones(preferencias, catalogo_prueba)
        assert recomendados == []  # Si no hay cursos de la categoría pedida, la lista debe estar vacía y no lanzar error
        assert altos == []         # Tampoco puede haber altamente recomendados si no hay recomendados base

    def test_compatibilidad_nivel(self, catalogo_prueba):
        """Test de compatibilidad de nivel entre usuario y curso."""
        preferencias = {
            "categoria": "Programacion",
            "nivel": "Intermedio",      # Usuario Intermedio (valor ordinal 2): puede ver cursos con nivel <= 2
            "presupuesto_max": 200.0,
            "tiempo_disponible": 100,
        }
        recomendados, altos = inferir_recomendaciones(preferencias, catalogo_prueba)
        # La regla de compatibilidad: nivel_curso <= nivel_usuario
        # Curso A: Principiante (1) <= Intermedio (2) → compatible ✓
        # Curso B: Intermedio (2)   <= Intermedio (2) → compatible ✓
        # Curso D: Principiante (1) <= Intermedio (2) → compatible ✓
        # Curso C: es de Datos, no de Programacion   → descartado por categoría antes de llegar aquí
        assert len(recomendados) == 3  # A, B y D pasan; C queda fuera por categoría