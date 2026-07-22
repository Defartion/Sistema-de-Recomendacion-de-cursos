from dataclasses import dataclass, field  # dataclass genera automáticamente el constructor y otros métodos; field permite configurar atributos especiales como listas
from typing import List, Any  # List se usa para declarar que un atributo es una lista de cierto tipo


@dataclass  # Este decorador convierte la clase en un dataclass: genera __init__ automáticamente a partir de los atributos declarados abajo
class Curso:
    """
    Representa un curso online en el sistema de recomendación.
    """
    # ── Atributos del curso (se llenan automáticamente por el @dataclass) ──
    id: int              # Identificador único del curso, coincide con el campo "id" del JSON
    nombre: str          # Nombre completo del curso
    categoria: str       # Área temática: Programacion, Datos, Diseno, Marketing, Negocios o Idiomas
    nivel: str           # Dificultad del curso: Principiante, Intermedio o Avanzado
    duracion_horas: int  # Cuántas horas dura el curso en total
    precio: float        # Costo en dólares; si es 0.0 el curso es gratuito
    modalidad: str       # Forma de cursarlo: "Asincrono" (a tu ritmo) o "Sincrono" (en vivo)
    plataforma: str      # Plataforma que ofrece el curso: Udemy, Coursera, Platzi, edX, etc.
    rating: float        # Calificación del curso en escala de 0.0 a 5.0
    url: str = ""        # Enlace directo al curso; valor por defecto vacío si no se proporciona
    tags: List[str] = field(default_factory=list)  # Lista de temas que cubre el curso (ej: ["python", "machine learning"]); default_factory=list crea una lista nueva para cada instancia, evitando que todas compartan la misma lista

    def __post_init__(self):
        """Validaciones básicas después de la inicialización."""
        # __post_init__ se ejecuta automáticamente justo después de que @dataclass crea el objeto,
        # antes de que ese objeto llegue a cualquier otra parte del sistema

        if not (0.0 <= self.rating <= 5.0):  # Verifica que el rating esté dentro del rango válido
            raise ValueError("El rating debe estar entre 0.0 y 5.0")  # Si no, lanza un error que detiene la creación del objeto
        if self.duracion_horas <= 0:  # Un curso con duración de 0 o negativa no tiene sentido
            raise ValueError("La duración debe ser mayor a 0")
        if self.precio < 0:  # El precio nunca puede ser negativo
            raise ValueError("El precio no puede ser negativo")

        # Normalizar URL vacía o inválida
        if not self.url or not self.url.startswith(("http://", "https://")):  # Si la URL está vacía o no empieza con http:// o https:// se considera inválida
            self.url = ""  # Se reemplaza por una cadena vacía para que el template no intente abrir un enlace roto

    def to_dict(self) -> dict:
        """
        Convierte la instancia a un diccionario serializable.

        Returns:
            dict: Representación en diccionario del curso.
        """
        # Jinja2 (los templates HTML) no puede leer objetos Python directamente,
        # por eso necesitamos convertir el objeto a un diccionario antes de enviarlo
        return {
            "id": self.id,
            "nombre": self.nombre,
            "categoria": self.categoria,
            "nivel": self.nivel,
            "duracion_horas": self.duracion_horas,
            "precio": self.precio,
            "modalidad": self.modalidad,
            "plataforma": self.plataforma,
            "rating": self.rating,
            "url": self.url,
            "tags": self.tags,  # La lista de tags se incluye tal cual para que el template pueda iterar sobre ella
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Curso":
        """
        Crea una instancia de Curso desde un diccionario.

        Args:
            data (dict): Diccionario con los atributos del curso.

        Returns:
            Curso: Instancia de la clase Curso.
        """
        # @classmethod significa que este método pertenece a la clase, no a una instancia.
        # Se llama como Curso.from_dict(data) sin necesidad de crear un objeto primero.
        # Es el constructor alternativo que usa el controller para convertir el JSON en objetos Curso.
        return cls(  # cls es la propia clase Curso; llamarlo así es equivalente a escribir Curso(...)
            id=data["id"],                      # Usa [] porque estos campos son obligatorios; si faltan en el JSON lanzará un KeyError
            nombre=data["nombre"],
            categoria=data["categoria"],
            nivel=data["nivel"],
            duracion_horas=data["duracion_horas"],
            precio=data["precio"],
            modalidad=data["modalidad"],
            plataforma=data["plataforma"],
            rating=data["rating"],
            url=data.get("url", ""),            # Usa .get() porque url es opcional; si no existe en el JSON devuelve "" en lugar de lanzar error
            tags=data.get("tags", []),          # Igual que url: si el curso no tiene tags en el JSON, se asigna una lista vacía por defecto
        )

    def __eq__(self, other: object) -> bool:
        """Dos cursos son iguales si tienen el mismo id."""
        if not isinstance(other, Curso):  # Verifica que se esté comparando con otro objeto Curso y no con otro tipo de dato
            return NotImplemented          # Si no es un Curso, Python intentará la comparación al revés con el otro objeto
        return self.id == other.id         # Dos cursos son idénticos si y solo si tienen el mismo id, sin importar si otros campos difieren

    def __hash__(self) -> int:
        """Permite usar instancias de Curso en conjuntos y como claves."""
        # Sin __hash__, Python no permitiría meter objetos Curso en un set ni usarlos como claves de diccionario.
        # El controller usa sets de cursos para buscar coincidencias en O(1) al cruzar resultados de logic_rules y processor.
        return hash(self.id)  # Genera un número entero único basado en el id; dos cursos con el mismo id producirán el mismo hash