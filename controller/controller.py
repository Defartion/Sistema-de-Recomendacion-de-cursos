"""
Modulo controlador (paradigma imperativo/OO).
"""

import json
import logging
import os
import traceback
from typing import List
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from models.curso import Curso
from processor.processor import procesar_recomendaciones
from logic_rules.logic_rules import inferir_recomendaciones

logger = logging.getLogger(__name__)
controller_bp = Blueprint("controller", __name__, template_folder="ui/templates")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CURSOS_JSON = os.path.join(BASE_DIR, "data", "cursos.json")

_catalogo_cursos: List[Curso] = []


def _cargar_catalogo() -> List[Curso]: #Cargar el catálogo de cursos desde un archivo JSON y cachearlo en memoria
    global _catalogo_cursos #Usamos la variable global para cachear el catálogo de cursos
    if not _catalogo_cursos: #Si el catalogo de cursos está vacio se empiza a ejecutar lo siguiente
        with open(CURSOS_JSON, "r", encoding="utf-8") as f: #Abrimos el archivo JSON que contiene los cursos (está contenido en CURSOS_JSON) y se usa "r" para leer el archivo y "utf-8" para codificarlo, asiganos el seudomio a lo anteriorior con "f"
            data = json.load(f) #Cargamos el contenido del archivo JSON en la variable "data" usando json.load(f)
        _catalogo_cursos = [Curso.from_dict(c) for c in data] # Creamos una lista de objetos Curso a partir de los diccionarios en "data" usando una comprensión de listas y el método from_dict de la clase Curso, y asignamos esta lista a la variable global _catalogo_cursos
 
    return list(_catalogo_cursos) #Retornar copia para evitar mutación del catálogo cached



PROFESIONES_JSON = os.path.join(BASE_DIR, "data", "profesiones.json") #Buscar el archivo profesiones.json en la carpeta data y asignarlo a la variable PROFESIONES_JSON

def _cargar_profesiones() -> dict: #Cargar las categorias de profesiones desde un archivo JSON
    if os.path.exists(PROFESIONES_JSON): #Si el archivo profesiones.json existe, se ejecuta lo siguiente
        with open(PROFESIONES_JSON, "r", encoding="utf-8") as f: #Abrimos el archivo JSON que contiene las profesiones (está contenido en PROFESIONES_JSON) y se usa "r" para leer el archivo y "utf-8" para codificarlo, asiganos el seudomio a lo anteriorior con "f"
            return json.load(f) #Cargamos el contenido del archivo JSON en la variable "data" usando json.load(f) y lo retornamos
    return {} #Si el archivo profesiones.json no existe, retornamos un diccionario vacío


def _categorias_por_profesion(profesion: str) -> List[str]: #Dada una profesion, retorna las categorias de cursos relacionadas a esa profesion
    profesion_lower = profesion.lower() #Convertimos la profesion a minusculas para hacer la busqueda insensible a mayusculas/minusculas
    profesion_map = _cargar_profesiones() #Cargamos el diccionario de profesiones y categorias desde el archivo JSON
    categorias = [] #Inicializamos una lista vacia para almacenar las categorias relacionadas a la profesion
    for keyword, cats in profesion_map.items(): #Iteramos sobre el diccionario de profesiones y categorias, donde keyword es la profesion y cats es la lista de categorias relacionadas a esa profesion
        if keyword in profesion_lower: #Si la palabra clave (keyword) está contenida en la profesion del usuario (profesion_lower), se ejecuta lo siguiente
            for cat in cats: #Iteramos sobre la lista de categorias relacionadas a la profesion
                if cat not in categorias: #Si la catagoria no esta dentro de la lista de categorias
                    categorias.append(cat) #Agregamos la categoria a la lista de categorias
    return categorias #Retornamos la lista de categorias


@controller_bp.route("/") #Ruta principal del controlador (/)
def index():
    return render_template("index.html") #Si el usuario accede a la raiz del sitio web, muestra index.html


@controller_bp.route("/recomendar", methods=["POST"]) #Ruta para procesar la recomendacion de cursos, solo acepta el metodo POST
def recomendar(): #Esta función se ejecuta cuando el usuario envía el formulario.
    try:
        # Datos del onboarding
        nombre    = request.form.get("nombre", "").strip() #Obtenemos el valor del campo "nombre" del formulario, si no existe se asigna una cadena vacía y se eliminan espacios en blanco al inicio y al final
        edad      = request.form.get("edad", "").strip()
        sexo      = request.form.get("sexo", "").strip()
        profesion = request.form.get("profesion", "").strip()

        # Preferencias
        categoria  = request.form.get("categoria", "").strip() #Obtenemos el valor del campo "categoria" del formulario, si no existe se asigna una cadena vacía y se eliminan espacios en blanco al inicio y al final
        nivel      = request.form.get("nivel", "").strip()
        presupuesto = request.form.get("presupuesto", "0")
        tiempo     = request.form.get("tiempo", "0")
        modalidad  = request.form.get("modalidad", "").strip()
        tags       = request.form.get("tags", "").strip()

        # Mapear valores de display (UI) a valores de datos (JSON)
        MODALIDAD_MAP = {"A mi ritmo": "Asincrono", "En vivo": "Sincrono",
                         "Asincrona": "Asincrono", "Sincro": "Sincrono"} 
        #Si el usuario eligió "A mi ritmo" → internamente usar "Asincrono".
        #Si eligió "En vivo" → usar "Sincrono"
        modalidad_raw = modalidad # Guardamos el valor original de modalidad para mostrarlo en la UI
        modalidad = MODALIDAD_MAP.get(modalidad, modalidad) #Si la modalidad no está en el diccionario MODALIDAD_MAP, se mantiene el valor original

        try:
            presupuesto_val = float(presupuesto) if presupuesto else 0.0 #A presupuesto_val se asigna el presupuesto que ingresó el usuario, si el usuario no ingresó un valor para presupuesto, se asigna 0.0
            tiempo_val = int(float(tiempo)) if tiempo else 0 #A tiempo_val se asigna el presupuesto que ingresó el usuario, si el usuario no ingresó un valor para tiempo, se asigna 0
        except ValueError:
            flash("Los valores de presupuesto y tiempo deben ser numericos.", "error")
            return redirect(url_for("controller.index")) #Redirige al usuario a la página principal si hay un error en la conversión de presupuesto o tiempo a números

        if not all([nombre, nivel, tiempo_val]):
            flash("Por favor completa todos los campos obligatorios.", "error")
            return redirect(url_for("controller.index"))
        #Redirige al usuario a la página principal si no se completaron todos los campos obligatorios

        if edad:
            try:
                edad_num = int(edad) #Convertimos la edad a un número entero para validarla
                if edad_num < 10 or edad_num > 100: 
                    flash("La edad debe estar entre 10 y 100 años.", "error")
                    return redirect(url_for("controller.index"))
                #Si la edad es menor a 10 o mayor a 100, se muestra un mensaje de error y se redirige al usuario a la página principal
            except ValueError:
                flash("La edad debe ser un número entero válido.", "error")
                return redirect(url_for("controller.index"))
            #Si la edad no es un número entero válido, se muestra un mensaje de error y se redirige al usuario a la página principal

        if presupuesto_val < 0 or tiempo_val <= 0:#
            flash("El presupuesto debe ser positivo y el tiempo mayor a 0.", "error")
            return redirect(url_for("controller.index"))
        #Si la edad es menor a 10 o mayor a 100, se muestra un mensaje de error y se redirige al usuario a la página principal

        # validador de solo gratuitos
        solo_gratuitos = request.form.get("solo_gratuitos", "")
        if solo_gratuitos:
            presupuesto_val = 0.0
        #Si el usuario selecciona la opción de "solo gratuitos", se establece el presupuesto máximo en 0.0 para filtrar solo cursos gratuitos

        tags_list = [t.strip() for t in tags.split(",") if t.strip()] #Toma un texto con etiquetas separadas por comas y lo convierte en una lista limpia.
        catalogo = _cargar_catalogo() #Trae todos los cursos desde cursos.json usando la función previa de "_cargar_catalogo"

        # ── Altamente recomendados: cursos que cumplen todos los criterios ──
        preferencias = { #Agrupa los criterios ingresados por el usuario en una sola estructura.
            "categoria": categoria, #Guarda la categoría de curso que busca el usuario.
            "nivel": nivel,
            "presupuesto_max": presupuesto_val,
            "tiempo_disponible": tiempo_val,
        } 
        recomendados_logicos, altamente_recomendados = inferir_recomendaciones( 
        #Compara las preferencias con el catálogo y separa los resultados según su nivel de coincidencia.
            preferencias, # Envía los criterios del usuario al sistema de recomendación. 
            catalogo  # Envía la lista completa de cursos disponibles.
        )  

        resultados_funcionales = procesar_recomendaciones(
            catalogo, 
            presupuesto=presupuesto_val, 
            tiempo=tiempo_val,
            modalidad=modalidad, 
            tags_usuario=tags_list, 
            nivel_usuario=nivel, 
            top_n=50
        ) #Procesa el catálogo aplicando los filtros del usuario y devuelve hasta 50 cursos puntuados.

        ids_logicos = {c.id for c in recomendados_logicos}
        #Obtiene los identificadores de los cursos considerados recomendables por las reglas lógicas.
        ids_altos   = {c.id for c in altamente_recomendados}
        #Obtiene los identificadores de los cursos considerados altamente recomendables por las reglas lógicas.

        recomendaciones = [] #Lista que almacenará los cursos recomendados junto con su puntuación y etiquetas de lógica.
        for res in resultados_funcionales: #Recorre cada resultado obtenido mediante el procesamiento funcional.
            curso = res["curso"]  #Extrae el objeto curso del resultado actual.
            recomendaciones.append({
                "curso": curso,
                "score": res["score"],
                "es_logico": curso.id in ids_logicos,
                "es_alto": curso.id in ids_altos,
            }) #Agrega un diccionario a la lista de recomendaciones que contiene el curso, su puntuación y banderas que indican si fue recomendado por las reglas lógicas y si es altamente recomendado.

        recomendaciones.sort(key=lambda x: (not x["es_alto"], -x["score"])) #Ordena la lista de recomendaciones primero por si son altamente recomendadas (es_alto) y luego por la puntuación (score) en orden descendente.
        
        mejor_valorados = [
            {"curso": c,  # Curso seleccionado.
             "score": c.rating / 5.0, # Convierte la valoración a una escala de 0 a 1.
             "es_logico": False, # No depende de las reglas lógicas.
             "es_alto": True  # Se destaca como una recomendación importante.
             }
            for c in catalogo if c.rating >= 4.7 # Recorre el catalogo en busca de cursos con rating 4.7 o más
        ]
        
        mejor_valorados.sort(
            key=lambda x: -x["curso"].rating
        ) #Ordena los cursos desde la valoración más alta hasta la más baja.
        

        # ── Carruseles por categoria: TODOS los cursos del catalogo agrupados ──
        categorias_orden = [
            "Programacion", 
            "Datos", 
            "Diseno", 
            "Marketing", 
            "Negocios", 
            "Idiomas"
        ] # Define el orden en que se mostrarán las categorías en la interfaz.
        carruseles = {} # Crea un diccionario vacío para guardar los cursos agrupados por categoría.
        for cat in categorias_orden: # Recorre cada categoría respetando el orden definido.
            cursos_cat = [ # Selecciona los cursos que pertenecen a la categoría actual.
                {
                    "curso": c,
                    "score": c.rating / 5.0,
                    "es_logico": False, 
                    "es_alto": c.rating >= 4.5
                }
                for c in catalogo if c.categoria == cat # Recorre todos los cursos disponibles conservando solo aquellos que coinciden con la categoría actual.
            ]
            cursos_cat.sort(
                key=lambda x: -x["curso"].rating
            ) # Ordena los cursos de mayor a menor valoración.
            
            if cursos_cat:
                carruseles[cat] = cursos_cat
            # Guarda la categoría únicamente si contiene cursos.

        # ── Relacionados a la profesion ──
        cats_profesion = _categorias_por_profesion(profesion) if profesion else []
        # Obtiene las categorías de cursos relacionadas con la profesión del usuario, si se proporcionó una profesión.
        ids_recomendados = {r["curso"].id for r in recomendaciones}
        # Extrae los identificadores (id) de los cursos que ya fueron recomendados.

        relacionados_profesion = [] # Lista que almacenará cursos relacionados con la profesión del usuario.
        
        if cats_profesion: # Si se encontraron categorías relacionadas con la profesión del usuario, se procede a buscar cursos en esas categorías.
            for curso in catalogo: # Recorre todos los cursos disponibles en el catálogo.
                if curso.categoria in cats_profesion and curso.id not in ids_recomendados: # Verifica si el curso pertenece a una de las categorías relacionadas con la profesión del usuario y si no ha sido recomendado previamente.
                    relacionados_profesion.append({
                        "curso": curso,
                        "score": curso.rating / 5.0,
                        "es_logico": False,
                        "es_alto": curso.rating >= 4.5,
                    }) # Agrega el curso a la lista de relacionados con la profesión, incluyendo su puntuación y banderas de lógica y alta recomendación.
            relacionados_profesion.sort(key=lambda x: -x["curso"].rating) #Ordena los cursos relacionados con la profesión de mayor a menor valoración.

        # Guardar busqueda en sesion para recuperar contexto despues
        session["ultima_busqueda"] = {
            "nombre": nombre,
            "edad": edad,
            "sexo": sexo,
            "profesion": profesion,
            "categoria": categoria,
            "nivel": nivel,
            "presupuesto": presupuesto_val,
            "tiempo": tiempo_val,
            "modalidad": modalidad_raw,
            "tags": tags_list,
        }
        
        # Contadores para la UI
        total_recomendaciones = len(recomendaciones) #Contador de cursos recomendados según las preferencias del usuario.
        total_relacionados = len(relacionados_profesion) #Contador de cursos relacionados con la profesión del usuario.
        total_mejor_valorados = len(mejor_valorados) #Contador de cursos con alta valoración (rating >= 4.7).

        return render_template(
            "resultado.html", #Muestra resultado.html.
            recomendaciones=recomendaciones,
            mejor_valorados=mejor_valorados,
            carruseles=carruseles,
            relacionados_profesion=relacionados_profesion,
            cats_profesion=cats_profesion,
            total_recomendaciones=total_recomendaciones,
            total_relacionados=total_relacionados,
            total_mejor_valorados=total_mejor_valorados,
            preferencias={
                "categoria": categoria,
                "nivel": nivel,
                "presupuesto": presupuesto_val,
                "tiempo": tiempo_val,
                "modalidad": modalidad_raw,
                "tags": tags_list,
            }, #Inserta dentro de la plantilla los datos como recomendaciones, carruseles, preferencias, presupuesto.
            usuario={
                "nombre": nombre,
                "edad": edad,
                "sexo": sexo,
                "profesion": profesion,
            } #Inserta dentro de la plantilla los datos del usuario.
        ) # Envía los resultados, preferencias y datos del usuario a la plantilla para mostrar la página final.

    except Exception as e: # Captura cualquier error, lo registra, avisa al usuario y lo redirige al inicio.
        logger.error(f"Error al procesar recomendacion: {e}\n{traceback.format_exc()}")
        flash("Ocurrio un error al procesar la solicitud. Por favor intenta de nuevo.", "error")
        return redirect(url_for("controller.index"))