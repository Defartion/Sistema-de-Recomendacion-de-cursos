# Dominio del Problema: Sistema de Recomendación de Cursos Online

## 1. Entidad Principal

**Curso online** — representa una oferta educativa disponible en plataformas digitales.

### Atributos del Curso

| Atributo | Tipo | Descripción | Ejemplo |
|----------|------|-------------|---------|
| `id` | int | Identificador único | 1 |
| `nombre` | str | Título del curso | "Python para Principiantes" |
| `categoria` | str | Categoría temática | Programación, Diseño, Datos, Marketing, Negocios, Idiomas |
| `nivel` | str | Nivel de dificultad | Principiante, Intermedio, Avanzado |
| `duracion_horas` | int | Duración estimada en horas | 30 |
| `precio` | float | Precio en USD | 49.99 |
| `modalidad` | str | Síncrono / Asíncrono | Asíncrono |
| `plataforma` | str | Plataforma que ofrece el curso | Udemy, Coursera, edX |
| `rating` | float | Puntuación (0.0 – 5.0) | 4.5 |
| `tags` | list[str] | Palabras clave descriptivas | ["python", "programación", "básico"] |

---

## 2. Datos de Entrada del Usuario (Preferencias)

El usuario interactúa con el sistema proporcionando sus preferencias de búsqueda:

| Preferencia | Tipo | Descripción |
|-------------|------|-------------|
| `categoria` | str | Categoría de interés del usuario |
| `nivel` | str | Nivel actual de conocimiento del usuario |
| `presupuesto_max` | float | Máximo dinero que puede invertir (USD) |
| `tiempo_disponible` | int | Horas disponibles para estudiar |
| `modalidad` | str | Síncrono o Asíncrono (preferida) |
| `palabras_clave` | list[str] | (Opcional) Tags de interés |

---

## 3. Reglas Lógicas de Recomendación

### 3.1. Reglas en Lenguaje Natural

1. **Regla de Categoría y Nivel:** Un curso es **recomendable** si su `categoria` coincide con el interés del usuario Y su `nivel` es compatible con la progresión lógica de aprendizaje (igual o un nivel anterior al del usuario).

2. **Regla de Presupuesto:** Un curso es **recomendable** si su `precio` es **menor o igual** al `presupuesto_max` del usuario.

3. **Regla de Tiempo:** Un curso es **recomendable** si su `duracion_horas` es **menor o igual** al `tiempo_disponible` del usuario.

4. **Regla de Alta Recomendación:** Un curso es **altamente recomendado** si cumple las 3 reglas anteriores Y su `rating` es **mayor o igual a 4.0**.


### 3.2. Representación en Pseudo-Lógica (Datalog/Kanren)

```
% Hechos
hecho(id, nombre, categoria, nivel, duracion, precio, modalidad, plataforma, rating, tags).

% Regla 1: Compatibilidad de categoría y nivel
recomendable(C) :- hecho(C, _, Cat, Nivel, _, _, _, _, _, _),
                   interes_usuario(Cat),
                   nivel_compatible(Nivel, NivelUsuario).

% Regla 2: Compatibilidad de presupuesto
recomendable(C) :- hecho(C, _, _, _, _, Precio, _, _, _, _),
                   Precio =< PresupuestoMax.

% Regla 3: Compatibilidad de tiempo
recomendable(C) :- hecho(C, _, _, _, Duracion, _, _, _, _, _),
                   Duracion =< TiempoDisponible.

% Regla 4: Alta recomendación
altamente_recomendado(C) :- recomendable(C),
                            hecho(C, _, _, _, _, _, _, _, Rating, _),
                            Rating >= 4.0.

```

---

## 4. Categorías Representadas en la Base de Datos

| Categoría | Cantidad de Cursos | Niveles Cubiertos |
|-----------|-------------------|-------------------|
| Programación | 15 | Principiante, Intermedio, Avanzado |
| Datos | 10 | Principiante, Intermedio, Avanzado |
| Diseño | 8 | Principiante, Intermedio, Avanzado |
| Marketing | 7 | Principiante, Intermedio |
| Negocios | 8 | Principiante, Intermedio |
| Idiomas | 6 | Principiante, Intermedio |

**Total de cursos en la base de conocimiento:** 54 cursos.

---

## 5. Objetivo del Sistema

El sistema debe permitir al usuario:

1. Ingresar sus preferencias personales (categoría, nivel, presupuesto, tiempo, modalidad).
2. Consultar cursos disponibles que se ajusten a dichas preferencias.
3. Recibir una recomendación final ordenada por relevancia, generada combinando:
   - **Filtrado funcional** (presupuesto, tiempo, modalidad).
   - **Inferencia lógica** (reglas de compatibilidad de categoría/nivel y alta recomendación).
   - **Orquestación imperativa** (flujo de control, manejo de excepciones, respuesta HTTP).
\n## Base de conocimiento\n\nEl sistema cuenta con un catálogo de **57 cursos** distribuidos en 6 categorias principales:\n\n| Categoría | No. de Cursos |\n|-----------|---------------|\n| Programacion | 10 |\n| Datos | 10 |\n| Diseno | 10 |\n| Marketing | 9 |\n| Negocios | 9 |\n| Idiomas | 9 |\n| **Total** |volatile | **57** |\n