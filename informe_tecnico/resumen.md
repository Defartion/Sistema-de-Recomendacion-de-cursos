# Resumen Técnico del Proyecto: Sistema de Recomendación de Cursos Online

## 1. Introducción

Este documento presenta un resumen técnico del proyecto "Sistema de Recomendación de Cursos Online", destacando su propósito, las tecnologías clave utilizadas, las justificaciones detrás de estas elecciones y las razones por las cuales otras alternativas no fueron implementadas. El proyecto fue desarrollado con un enfoque académico para demostrar la integración de múltiples paradigmas de programación en una aplicación funcional.

## 2. Resumen del Proyecto

El proyecto consiste en un sistema web inteligente diseñado para recomendar cursos online a usuarios, basándose en sus preferencias. Su característica distintiva es la **integración explícita de tres paradigmas de programación**: imperativo/orientado a objetos, funcional y lógico. El sistema permite a los usuarios ingresar sus preferencias (categoría, nivel, presupuesto, tiempo y modalidad) y genera recomendaciones personalizadas. [1]

**Alcance del Proyecto:**

*   Base de conocimiento con 54 cursos (aunque la documentación inicial mencionaba 15). [1] [2]
*   Interfaz web para la interacción del usuario.
*   Motor de recomendación que combina reglas lógicas y filtrado funcional.
*   Pruebas unitarias e integrales.

**Exclusiones Notables:**

*   Autenticación de usuarios.
*   Base de datos relacional persistente.
*   Despliegue en producción. [1]

## 3. Tecnologías Utilizadas

El proyecto se construyó principalmente con **Python** y un conjunto de librerías y frameworks específicos para cada paradigma y la interfaz web.

| Categoría | Tecnología | Versión Clave | Propósito en el Proyecto |
|:----------|:-----------|:--------------|:-------------------------|
| **Lenguaje de Programación** | Python | 3.11+ | Lenguaje principal para todo el desarrollo backend. [1] |
| **Framework Web** | Flask | >=3.0.0 | Microframework para la gestión de rutas HTTP, validación y orquestación (Paradigma Imperativo/OO). [1] [3] |
| **Programación Lógica** | kanren | >=0.3.0 | Librería para la implementación de reglas de inferencia y razonamiento lógico. [1] [3] |
| **Motor de Plantillas** | Jinja2 | (Integrado con Flask) | Renderizado de las vistas HTML dinámicas. [1] |
| **Frontend** | HTML, CSS, JavaScript (Vanilla) | N/A | Interfaz de usuario, estilos y lógica interactiva del lado del cliente. [4] |
| **Almacenamiento de Datos** | JSON | N/A | Almacenamiento local de la base de conocimiento de cursos. [2] |
| **Testing** | Pytest | >=8.0.0 | Framework para la ejecución de pruebas unitarias e integrales. [1] [3] |

## 4. Justificación de las Elecciones y Alternativas No Utilizadas

La selección de tecnologías se basó en la necesidad de demostrar claramente la aplicación de los diferentes paradigmas de programación, priorizando la simplicidad y el control explícito sobre la abstracción excesiva o la complejidad de un entorno de producción.

### 4.1 Framework Web: Flask

*   **Elección**: **Flask** fue seleccionado por su naturaleza de microframework, que ofrece **ligereza** y una **curva de aprendizaje baja**. Permite un **control explícito del flujo de la aplicación**, lo cual fue ideal para evidenciar el paradigma imperativo/orientado a objetos en el módulo `controller.py` sin abstracciones que ocultaran la lógica de ejecución. [1]
*   **Alternativas No Utilizadas**: Frameworks más robustos como **Django** o **FastAPI** no fueron elegidos. Django, aunque completo, podría haber introducido demasiada abstracción y complejidad para un proyecto académico centrado en la demostración de paradigmas. FastAPI, aunque moderno y eficiente, no ofrecía una ventaja significativa en el contexto de este proyecto donde el rendimiento no era la preocupación principal y la demostración de un control de flujo más tradicional era deseada.

### 4.2 Programación Lógica: kanren

*   **Elección**: **kanren** se eligió como la librería de programación lógica debido a su **compatibilidad con Python 3.11+** y su **sintaxis declarativa basada en relaciones**. Esto permitió modelar de forma natural las reglas de recomendación (e.g., "si cumple X e Y, entonces Z") dentro del entorno Python, facilitando la integración con el resto del sistema. [1]
*   **Alternativas No Utilizadas**: Otros motores de programación lógica como **Prolog** o **Datalog** no fueron directamente integrados. Si bien son lenguajes potentes para la lógica, habrían requerido una integración más compleja con Python o la necesidad de aprender un nuevo lenguaje, lo que se consideró fuera del alcance para un proyecto que buscaba demostrar el paradigma lógico *dentro* de Python. El informe técnico menciona que la integración de `kanren` con estructuras de datos complejas (`Curso` objetos) requirió adaptaciones, sugiriendo que un motor lógico más avanzado podría haber manejado esto de forma más nativa, pero a costa de mayor complejidad de integración. [1]

### 4.3 Frontend: HTML, CSS y JavaScript (Vanilla)

*   **Elección**: Se optó por un frontend tradicional utilizando **HTML, CSS y JavaScript puro (Vanilla)**, complementado con el motor de plantillas **Jinja2** de Flask. Esta elección mantuvo la simplicidad y el enfoque en la lógica de backend y la integración de paradigmas, sin añadir la complejidad de un framework frontend moderno. [4]
*   **Alternativas No Utilizadas**: Frameworks de JavaScript como **React, Vue o Angular** no se utilizaron. La implementación de un Single Page Application (SPA) con estas tecnologías habría desviado el foco del proyecto hacia el desarrollo frontend y la gestión de estados complejos, lo cual no era el objetivo principal. La simplicidad del frontend actual fue suficiente para la demostración académica.

### 4.4 Persistencia de Datos: Archivos JSON

*   **Elección**: La base de conocimiento de cursos se almacenó en un archivo **JSON** (`cursos.json`). Esta decisión se tomó porque el proyecto **no incluía una base de datos relacional persistente** ni despliegue en producción, lo que hacía que un archivo local fuera una solución sencilla y adecuada para el alcance académico. [1] [2]
*   **Alternativas No Utilizadas**: Bases de datos relacionales como **PostgreSQL** o **MySQL**, o bases de datos NoSQL como **MongoDB**, no fueron implementadas. Su inclusión habría añadido una capa de complejidad en la configuración, ORM/ODM y gestión de esquemas que no era esencial para los objetivos de demostración de paradigmas del proyecto. Para un entorno de producción, una base de datos sería indispensable.

### 4.5 Testing: Pytest

*   **Elección**: **Pytest** fue seleccionado por su facilidad de uso, su sintaxis concisa y su capacidad para manejar pruebas unitarias y de integración de manera eficiente en Python. [1]
*   **Alternativas No Utilizadas**: El módulo `unittest` de Python, aunque es parte de la biblioteca estándar, a menudo se considera más verboso que Pytest para escribir pruebas, lo que hizo que Pytest fuera la opción preferida para este proyecto.

## 5. Conclusiones

El proyecto logró integrar exitosamente los paradigmas imperativo/orientado a objetos, funcional y lógico en un sistema de recomendación de cursos. La arquitectura modular y la elección de tecnologías ligeras y controlables como Flask y kanren permitieron una clara demostración de cada paradigma. Las exclusiones de funcionalidades de producción (autenticación, base de datos persistente, despliegue) fueron conscientes y alineadas con el objetivo académico del proyecto. [1]

## 6. Referencias

[1] Informe Técnico del Proyecto: `/home/ubuntu/proyecto_analisis/Proyecto/informe_tecnico/informe.md`
[2] Archivo de Datos de Cursos: `/home/ubuntu/proyecto_analisis/Proyecto/data/cursos.json`
[3] Archivo de Requisitos: `/home/ubuntu/proyecto_analisis/Proyecto/requirements.txt`
[4] Plantilla de Interfaz de Usuario: `/home/ubuntu/proyecto_analisis/Proyecto/ui/templates/index.html`
