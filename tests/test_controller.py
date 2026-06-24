"""
Pruebas de integracion para el controlador Flask (paradigma imperativo/OO).
"""

import pytest
from app import crear_app


@pytest.fixture
def client():
    """Cliente de prueba de Flask."""
    app = crear_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestRutasBasicas:
    def test_get_index_status_200(self, client):
        """Test que la pagina principal responde con 200."""
        response = client.get("/")
        assert response.status_code == 200
        assert b"EduPath" in response.data

    def test_get_index_contiene_formulario(self, client):
        """Test que la pagina principal contiene el formulario."""
        response = client.get("/")
        assert b"form" in response.data
        assert b"categoria" in response.data
        assert b"nivel" in response.data


class TestRecomendaciones:
    def test_post_recomendar_con_datos_validos(self, client):
        """Test de recomendacion con datos validos."""
        datos = {
            "categoria": "Programacion",
            "nivel": "Principiante",
            "presupuesto": "100",
            "tiempo": "50",
            "modalidad": "Asincrono",
            "tags": "python",
        }
        response = client.post("/recomendar", data=datos, follow_redirects=True)
        assert response.status_code == 200
        assert b"Recomendaciones" in response.data or b"resultados" in response.data.lower()

    def test_post_recomendar_campos_vacios_redirecciona(self, client):
        """Test que campos vacios redireccionan con mensaje de error."""
        datos = {
            "categoria": "",
            "nivel": "",
            "presupuesto": "",
            "tiempo": "",
            "modalidad": "",
        }
        response = client.post("/recomendar", data=datos, follow_redirects=True)
        assert response.status_code == 200

    def test_post_recomendar_presupuesto_invalido(self, client):
        """Test que presupuesto no numerico muestra error."""
        datos = {
            "categoria": "Programacion",
            "nivel": "Principiante",
            "presupuesto": "abc",
            "tiempo": "20",
            "modalidad": "Asincrono",
        }
        response = client.post("/recomendar", data=datos, follow_redirects=True)
        assert response.status_code == 200

    def test_post_recomendar_valores_negativos(self, client):
        """Test que valores negativos muestran error."""
        datos = {
            "categoria": "Programacion",
            "nivel": "Principiante",
            "presupuesto": "-50",
            "tiempo": "0",
            "modalidad": "Asincrono",
        }
        response = client.post("/recomendar", data=datos, follow_redirects=True)
        assert response.status_code == 200
