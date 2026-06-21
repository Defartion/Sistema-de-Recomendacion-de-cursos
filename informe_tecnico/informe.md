# Informe Tecnico

## Sistema de Recomendacion Inteligente de Cursos Online

---

**Universidad**: [Nombre de la Universidad]
**Curso**: Lenguajes de Programacion
**Docente**: [Nombre del Docente]
**Equipo**: Equipo 4
**Integrantes**:
- [Nombre Apellido 1]
- [Nombre Apellido 2]
- [Nombre Apellido 3]
- [Nombre Apellido 4]
**Fecha**: [Fecha de entrega]

---

## 1. Introduccion

### Contexto del Problema

En la actualidad, el e-learning ha experimentado un crecimiento exponencial, ofreciendo a los usuarios una amplia gama de cursos online en diversas plataformas como Coursera, Udemy, edX y Platzi. Sin embargo, esta abundancia de opciones genera un problema significativo: la dificultad para elegir el curso mas adecuado segun las necesidades, nivel de conocimiento y recursos de cada persona.

La saturacion de la oferta educativa online representa una barrera para el aprendizaje efectivo. Los usuarios pierden tiempo valioso evaluando opciones que no siempre se alinean con sus objetivos, presupuesto o disponibilidad horaria. Esta problematica justifica la necesidad de un sistema inteligente que, a partir de las preferencias del usuario, pueda filtrar, evaluar y recomendar cursos de manera personalizada y eficiente.

### Proposito del Sistema

El proposito de este proyecto es desarrollar un sistema web de recomendacion inteligente de cursos online que integre de manera explicita y diferenciada tres paradigmas de programacion: imperativo/orientado a objetos, funcional y logico. El sistema permite a los usuarios ingresar sus preferencias (categoria de interes, nivel de conocimiento, presupuesto, tiempo disponible y modalidad) y recibe una recomendacion final basada en la aplicacion conjunta de reglas logicas, filtrado funcional y orquestacion imperativa.

### Alcance

El sistema incluye:
- Base de conocimiento con 15 cursos reales en 6 categorias.
- Interfaz web funcional para ingreso de preferencias.
- Motor de recomendacion basado en reglas logicas de inferencia.
- Filtrado y ranking funcional de cursos.
- Pruebas unitarias e integrales para cada modulo.

No incluye: autenticacion de usuarios, base de datos relacional persistente, ni despliegue en produccion.

---

## 2. Fundamentacion Teorica

### 2.1 Paradigma Imperativo

El paradigma imperativo se basa en el concepto de estado y secuencia de instrucciones que modifican ese estado a traves de sentencias de asignacion, control de flujo (condicionales, bucles) y procedimientos [Sebesta, 2019]. Es el paradigma mas natural y directo, donde el programador describe paso a paso como alcanzar un resultado deseado mediante cambios en el estado del programa.

En el contexto de este proyecto, el paradigma imperativo se evidencia en el modulo controlador (`controller.py`), donde se maneja el flujo de peticiones HTTP, validacion de datos, manejo de excepciones y la orquestacion entre los diferentes modulos del sistema. El uso de estructuras de control, variables mutables y procedimientos secuenciales caracteriza esta implementacion.

### 2.2 Paradigma Funcional

El paradigma funcional trata la computacion como la evaluacion de funciones matematicas y evita el cambio de estado y datos mutables [Hudak, 1989]. Sus principios fundamentales incluyen funciones puras (mismos inputs siempre producen mismos outputs), transparencia referencial y el uso de funciones de orden superior como `map`, `filter` y `reduce`.

En nuestro sistema, el paradigma funcional se aplica en el modulo `processor.py`, donde todas las operaciones de filtrado, transformacion y ranking se implementan mediante funciones puras sin efectos secundarios. El uso explicito de `map`, `filter` y `reduce` evidencia la aplicacion de este paradigma para procesar el catalogo de cursos de manera declarativa y componible.

### 2.3 Paradigma Logico

El paradigma logico se basa en la logica formal y el razonamiento deductivo. Los programas consisten en un conjunto de hechos y reglas que definen relaciones entre entidades, y el sistema deriva nuevos conocimientos mediante inferencia logica [Sterling & Shapiro, 1994]. La programacion logica declara "que" debe hacerse en lugar de "como" hacerlo.

En este proyecto, el paradigma logico se implementa en `logic_rules.py` usando la libreria `kanren`. Se definen hechos (cursos con sus atributos) y reglas (compatibilidad de categoria, nivel, presupuesto y tiempo) para inferir recomendaciones validas. La declaracion de reglas como relaciones logicas permite un razonamiento declarativo sobre la base de conocimiento.

---

## 3. Diseno de la Solucion

### 3.1 Arquitectura Propuesta

La arquitectura sigue un patron Modelo-Vista-Controlador (MVC) adaptado para evidenciar claramente la separacion de responsabilidades entre los tres paradigmas:

```
Usuario -> Controller (Imperativo/OO) -> Processor (Funcional)
                                          -> Logic Rules (Logico)
                                              -> Vista HTML
```

**Diagrama de arquitectura:**

```
+-------------------+        +-------------------+        +-------------------+
|      Vista        |        |    Controller     |        |     Processor     |
|   (Jinja2/HTML)   | <----> |   (Flask/OO)      | <----> |  (Funcional)      |
+-------------------+        +-------------------+        +-------------------+
                                    |                              |
                                    v                              v
                             +-------------------+        +-------------------+
                             |   Logic Rules     |        |   Data (JSON)     |
                             |   (Logico)        |        |   cursos.json     |
                             +-------------------+        +-------------------+
```

**Justificacion tecnica:**

Se selecciono **Flask** como framework web por su ligereza, curva de aprendizaje baja y control explicito del flujo, lo cual resulta ideal para demostrar el paradigma imperativo sin abstracciones que oculten el control de ejecucion. Se selecciono **kanren** como libreria logica por su compatibilidad con Python 3.11+ y su sintaxis declarativa basada en relaciones, que permite modelar naturalmente las reglas de recomendacion tipo "si cumple X e Y, entonces Z".

### 3.2 Descripcion de Modulos

| Modulo | Archivo | Responsabilidad | Paradigma |
|--------|---------|----------------|-----------|
| Modelo | `models/curso.py` | Definicion de la entidad Curso con validaciones | OO |
| Controlador | `controller/controller.py` | Rutas HTTP, validacion, orquestacion, logging | Imperativo/OO |
| Procesador | `processor/processor.py` | Filtrado funcional, calculo de score, ranking | Funcional |
| Reglas Logicas | `logic_rules/logic_rules.py` | Inferencia de recomendaciones basada en reglas | Logico |
| Vista | `ui/templates/` | Plantillas HTML para formulario y resultados | Presentacion |
| Datos | `data/cursos.json` | Base de conocimiento de 15 cursos | Persistencia |

### 3.3 Prototipo Clickeable en Figma

[INSERTAR AQUÍ EL LINK AL PROTOTIPO DE FIGMA]

---

## 4. Implementacion

### 4.1 Uso del Paradigma Imperativo

El modulo `controller.py` gestiona el flujo completo de una peticion: recoleccion de datos, validacion, llamada a modulos funcionales y logicos, combinacion de resultados y renderizacion. Evidencia el uso de estado mutable, estructuras de control secuenciales y manejo de excepciones.

### 4.2 Uso del Paradigma Funcional

El modulo `processor.py` implementa operaciones puras de filtrado y ranking usando `map`, `filter`, `reduce` y expresiones `lambda`.

### 4.3 Uso del Paradigma Logico

El modulo `logic_rules.py` define reglas de inferencia sobre la base de conocimiento mediante la libreria `kanren`.

### 4.4 Integracion de los Modulos

Flujo end-to-end: El usuario envia una peticion POST con sus preferencias -> `controller.py` valida los datos -> Llama a `logic_rules.py` para identificar cursos que cumplen las reglas logicas -> Llama a `processor.py` para filtrar y rankear funcionalmente -> El controller combina ambos resultados (priorizando los que estan en ambas listas) -> Renderiza `resultado.html` con las recomendaciones finales.

---

## 5. Pruebas y Resultados

### Pruebas Automatizadas

Se desarrollaron 23 pruebas unitarias y de integracion usando `pytest`:

| Modulo de Tests | Casos de Prueba | Cobertura |
|-----------------|-----------------|-----------|
| `test_processor.py` | 11 | Filtrado funcional, score, ranking, pipeline completo |
| `test_logic_rules.py` | 6 | Reglas de inferencia, compatibilidad, alta recomendacion |
| `test_controller.py` | 6 | Rutas GET/POST, validacion, manejo de errores |
| **Total** | **23** | **100% funcionalidad** |

Todas las pruebas pasan exitosamente, demostrando la robustez y funcionalidad del sistema.

### Casos de Uso Manual

**Caso 1: Usuario principiante de programacion**
- Entrada: Categoria=Programacion, Nivel=Principiante, Presupuesto=$100, Tiempo=50h, Modalidad=Asincrono, Tags=python
- Resultado: El sistema recomienda "Python para Principiantes" como alta recomendacion (cumple todas las reglas, rating 4.5).

**Caso 2: Presupuesto limitado**
- Entrada: Categoria=Datos, Nivel=Intermedio, Presupuesto=$60, Tiempo=30h, Modalidad=Asincrono
- Resultado: Solo "Analisis de Datos con SQL" ($54.99) cumple el presupuesto, mientras que "Data Science con Python" ($79.99) queda fuera pero apareceria en recomendaciones ampliadas.

---

## 6. Conclusiones

### Logros

- Se logro integrar exitosamente los tres paradigmas de programacion en un unico sistema funcional.
- La arquitectura MVC adaptada permite una clara separacion de responsabilidades y facilita el mantenimiento.
- El sistema procesa recomendaciones en tiempo real con una base de conocimiento de 15 cursos.

### Dificultades Tecnicas

- La integracion de `kanren` con estructuras de datos complejas (objetos `Curso`) requirio adaptar el modelo a relaciones mas simples o usar representaciones intermedias.
- Garantizar la pureza funcional en el procesador implico evitar mutaciones del estado interno y del catalogo original.
- Balancear la expresividad de los tres paradigmas sin redundancia de logica fue un desafio de diseno.

### Aprendizajes

- La combinacion de paradigmas complementarios permite aprovechar las fortalezas de cada uno: control estructurado (imperativo), procesamiento declarativo (funcional) y razonamiento basado en reglas (logico).
- La modularizacion temprana y las pruebas unitarias rigurosas fueron fundamentales para detectar errores antes de la integracion.
- Documentar explicitamente donde y como se aplica cada paradigma resulta clave para proyectos academicos y de sustentacion.

---

## 7. Referencias

- Sebesta, R. W. (2019). *Concepts of Programming Languages* (12th ed.). Pearson.
- Hudak, P. (1989). *Conception, evolution, and application of functional programming languages*. ACM Computing Surveys, 21(3), 359-411.
- Sterling, L., & Shapiro, E. (1994). *The Art of Prolog: Advanced Programming Techniques* (2nd ed.). MIT Press.
- Documentacion oficial de Flask: https://flask.palletsprojects.com/
- Documentacion oficial de kanren: https://github.com/pythological/kanren
- van Rossum, G., & Drake, F. L. (2024). *The Python Language Reference*. Python Software Foundation.
