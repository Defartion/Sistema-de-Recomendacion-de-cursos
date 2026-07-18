# Sistema de Recomendacion de Cursos Online

## Descripcion del Proyecto

Sistema web de recomendacion inteligente de cursos online que integra tres paradigmas de programacion:

- **Paradigma Imperativo/Orientado a Objetos**: Control del flujo, validaciones y orquestacion HTTP.
- **Paradigma Funcional**: Filtrado, transformacion y ranking de datos con funciones puras.
- **Paradigma Logico**: Reglas de inferencia para recomendaciones basadas en hechos y relaciones.

## Integrantes del Equipo

- Basilio Vargas Christopher Jhon
- Castro Reyes Diego Leonardo
- Gutiérrez Chávez Diego
- Gutiérrez De La Cruz Kelly Judith
- Paul Luján Zavaleta Wilmer Enrique
- Pelaez Lopez Sebastian Nicolas


## Arquitectura del Proyecto

```
proyecto_recomendador_cursos/
|
|-- app.py                      # Punto de entrada Flask (imperativo/OO)
|-- controller/
|   |-- controller.py           # Paradigma IMPERATIVO/OO: rutas, flujo, eventos
|-- logic_rules/
|   |-- logic_rules.py          # Paradigma LOGICO: reglas, hechos, inferencias
|-- processor/
|   |-- processor.py            # Paradigma FUNCIONAL: funciones puras, map/filter/reduce
|-- models/
|   |-- curso.py                 # Clase Curso (OO) - estructura de datos
|-- ui/
|   |-- templates/               # HTML (Flask/Jinja2) - interfaz web
|   |   |-- base.html
|   |   |-- index.html
|   |   |-- resultado.html
|   |-- static/css/style.css    # Estilos
|-- data/
|   |-- cursos.json              # Base de conocimiento de 57 cursos 
|-- tests/
|   |-- test_processor.py        # Pruebas del modulo funcional
|   |-- test_logic_rules.py      # Pruebas del modulo logico
|   |-- test_controller.py       # Pruebas del controlador 
|-- docs/dominio.md              # Documentacion del dominio
|-- requirements.txt             # Dependencias
```

## Aplicacion de los Paradigmas

### Paradigma Imperativo/Orientado a Objetos
**Archivo**: `controller/controller.py`
- Control del flujo de peticiones HTTP.
- Validacion de datos de entrada.
- Manejo de excepciones y logging.
- Orquestacion entre los modulos funcional y logico.

### Paradigma Funcional
**Archivo**: `processor/processor.py`
- Funciones puras sin efectos secundarios (`filtrar_por_presupuesto`, `filtrar_por_modalidad`, `filtrar_por_tiempo`).
- Transformacion de datos con `map` y `filter`.
- Reduccion con `reduce` para extraccion de tags.
- Calculo de score con `map` y ordenamiento funcional.

### Paradigma Logico
**Archivo**: `logic_rules/logic_rules.py`
- Reglas de inferencia basadas en hechos (cursos) y preferencias del usuario.
- Uso de la libreria `kanren` para modelado logico.
- Determinacion de compatibilidad mediante reglas declarativas.

## Requisitos Previos

- Python 3.11 o superior
- pip (gestor de paquetes de Python)

## Instalacion

1. Clonar o copiar el proyecto:
```bash
cd proyecto_recomendador_cursos
```

2. Crear entorno virtual (opcional pero recomendado):
```bash
python -m venv venv
```

3. Activar el entorno virtual:
- Windows:
```bash
venv\Scripts\activate
```
- Linux/Mac:
```bash
source venv/bin/activate
```

4. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Ejecucion

### Iniciar la aplicacion
```bash
python app.py
```

La aplicacion estara disponible en: `http://127.0.0.1:5000`

### Ejecutar tests
```bash
pytest -v
```

## Uso de la Aplicacion

1. Acceder a `https://sistema-de-recomendacion-de-cursos-production.up.railway.app/` en el navegador.
2. Completar el formulario con las preferencias:
   - Categoria de interes
   - Nivel actual
   - Presupuesto maximo (USD)
   - Tiempo disponible (horas)
   - Modalidad preferida
   - Palabras clave (opcional)
3. Hacer clic en "Buscar Recomendaciones".
4. Visualizar los cursos recomendados ordenados por relevancia.

## Capturas de Pantalla

![Formulario de preferencias](docs/img/formulario.png)

## Estructura de Carpetas

- **controller/**: Modulo de control (paradigma imperativo/Orientado a Objetos)
- **processor/**: Modulo funcional (paradigma funcional)
- **logic_rules/**: Modulo logico (paradigma logico)
- **models/**: Modelos de datos
- **ui/**: Interfaz de usuario (templates y estilos)
- **data/**: Base de datos de cursos
- **tests/**: Pruebas unitarias y de integracion

