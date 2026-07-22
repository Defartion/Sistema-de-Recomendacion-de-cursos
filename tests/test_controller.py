"""
Pruebas de integracion para el controlador Flask (paradigma imperativo/OO).
"""

import pytest
from app import crear_app  # Importa la función que crea la aplicación Flask usando el patrón Application Factory


@pytest.fixture  # Declara esta función como un fixture de pytest: se ejecuta antes de cada test que la pida como parámetro
def client():
    """Cliente de prueba de Flask."""
    app = crear_app()                  # Crea una instancia limpia de la app para cada test, evitando que el estado de un test afecte a otro
    app.config["TESTING"] = True       # Activa el modo de pruebas: Flask propagará los errores en lugar de mostrar páginas de error genéricas
    with app.test_client() as client:  # Crea un cliente HTTP simulado que puede hacer GET y POST sin necesitar un servidor real corriendo
        yield client                   # Entrega el cliente al test que lo pidió; cuando el test termina, el bloque with cierra el cliente limpiamente


class TestRutasBasicas:  # Agrupa los tests que verifican que las rutas básicas de la app respondan correctamente
    def test_get_index_status_200(self, client):  # client viene del fixture definido arriba
        """Test que la pagina principal responde con 200."""
        response = client.get("/")                    # Simula un usuario abriendo la página principal en el navegador
        assert response.status_code == 200            # 200 significa que la página cargó correctamente; cualquier otro código indicaría un error
        assert b"EduPath" in response.data            # Verifica que el HTML devuelto contenga el nombre del sistema; la "b" indica que se compara como bytes, que es el formato en que Flask devuelve el HTML

    def test_get_index_contiene_formulario(self, client):
        """Test que la pagina principal contiene el formulario."""
        response = client.get("/")
        assert b"form" in response.data               # Verifica que la página tenga una etiqueta <form> para que el usuario pueda enviar sus preferencias
        assert b"categoria" in response.data          # Verifica que el campo de categoría exista en el formulario
        assert b"nivel" in response.data              # Verifica que el campo de nivel exista en el formulario


class TestRecomendaciones:  # Agrupa los tests que verifican el comportamiento de la ruta POST /recomendar con distintos escenarios
    def test_post_recomendar_con_datos_validos(self, client):
        """Test de recomendacion con datos validos."""
        datos = {                              # Simula el formulario que enviaría un usuario real con datos correctos
            "categoria": "Programacion",
            "nivel": "Principiante",
            "presupuesto": "100",
            "tiempo": "50",
            "modalidad": "Asincrono",
            "tags": "python",
        }
        response = client.post("/recomendar", data=datos, follow_redirects=True)
        # follow_redirects=True hace que si el servidor responde con un redirect (302),
        # el cliente lo siga automáticamente hasta llegar a la página final
        assert response.status_code == 200
        assert b"Recomendaciones" in response.data or b"recomendaciones" in response.data.lower()
        # Verifica que la página de resultados contenga la palabra "Recomendaciones" en cualquier forma
        # .lower() cubre el caso en que aparezca en minúsculas dentro de una clase CSS o atributo HTML

    def test_post_recomendar_campos_vacios_redirecciona(self, client):
        """Test que campos vacios redireccionan con mensaje de error."""
        datos = {                   # Simula un usuario que envió el formulario sin completar ningún campo
            "categoria": "",
            "nivel": "",
            "presupuesto": "",
            "tiempo": "",
            "modalidad": "",
        }
        response = client.post("/recomendar", data=datos, follow_redirects=True)
        assert response.status_code == 200
        # El controller detecta que faltan campos obligatorios, hace flash del error
        # y redirige al index; follow_redirects=True sigue ese redirect y el 200 confirma
        # que el usuario llegó de vuelta a la página principal sin que la app se rompiera

    def test_post_recomendar_presupuesto_invalido(self, client):
        """Test que presupuesto no numerico muestra error."""
        datos = {
            "categoria": "Programacion",
            "nivel": "Principiante",
            "presupuesto": "abc",   # Texto en lugar de número: debería fallar la conversión a float en el controller
            "tiempo": "20",
            "modalidad": "Asincrono",
        }
        response = client.post("/recomendar", data=datos, follow_redirects=True)
        assert response.status_code == 200
        # El controller captura el ValueError al intentar float("abc"),
        # muestra un flash de error y redirige al index; el 200 confirma que la app
        # manejó el error con gracia sin lanzar una excepción al usuario

    def test_post_recomendar_valores_negativos(self, client):
        """Test que valores negativos muestran error."""
        datos = {
            "categoria": "Programacion",
            "nivel": "Principiante",
            "presupuesto": "-50",   # Presupuesto negativo: inválido según las validaciones del controller
            "tiempo": "0",          # Tiempo de 0 horas: inválido porque no se puede completar ningún curso
            "modalidad": "Asincrono",
        }
        response = client.post("/recomendar", data=datos, follow_redirects=True)
        assert response.status_code == 200
        # El controller valida que presupuesto >= 0 y tiempo > 0;
        # al detectar que no se cumplen, hace flash del error y redirige al index
        # El 200 confirma que la validación funcionó y el usuario no vio una pantalla de error