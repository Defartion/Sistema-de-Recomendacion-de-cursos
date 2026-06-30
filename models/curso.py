"""
Módulo de modelo de dominio para el sistema de recomendación de cursos.

Este módulo contiene la definición de la entidad principal `Curso`,
tipos de datos y funciones utilitarias para la conversión entre
representaciones JSON y objetos Python.
"""

from dataclasses import dataclass, field
from typing import List, Any


@dataclass
class Curso:
    """
    Representa un curso online en el sistema de recomendación.

    Atributos:
        id (int): Identificador único del curso.
        nombre (str): Título del curso.
        categoria (str): Categoría temática (ej. Programación, Diseño, Datos).
        nivel (str): Nivel de dificultad (Principiante, Intermedio, Avanzado).
        duracion_horas (int): Duración estimada en horas.
        precio (float): Precio del curso en USD.
        modalidad (str): Modalidad de entrega (Síncrono / Asíncrono).
        plataforma (str): Plataforma que ofrece el curso.
        rating (float): Puntuación entre 0.0 y 5.0.
        tags (List[str]): Lista de etiquetas descriptivas.
    """
    id: int
    nombre: str
    categoria: str
    nivel: str
    duracion_horas: int
    precio: float
    modalidad: str
    plataforma: str
    rating: float
    url: str = ""
    tags: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Validaciones básicas después de la inicialización."""
        if not (0.0 <= self.rating <= 5.0):
            raise ValueError("El rating debe estar entre 0.0 y 5.0")
        if self.duracion_horas <= 0:
            raise ValueError("La duración debe ser mayor a 0")
        if self.precio < 0:
            raise ValueError("El precio no puede ser negativo")

    def to_dict(self) -> dict:
        """
        Convierte la instancia a un diccionario serializable.

        Returns:
            dict: Representación en diccionario del curso.
        """
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
            "tags": self.tags,
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
        return cls(
            id=data["id"],
            nombre=data["nombre"],
            categoria=data["categoria"],
            nivel=data["nivel"],
            duracion_horas=data["duracion_horas"],
            precio=data["precio"],
            modalidad=data["modalidad"],
            plataforma=data["plataforma"],
            rating=data["rating"],
            url=data.get("url", ""),
            tags=data.get("tags", []),
        )

    def __eq__(self, other: object) -> bool:
        """Dos cursos son iguales si tienen el mismo id."""
        if not isinstance(other, Curso):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        """Permite usar instancias de Curso en conjuntos y como claves."""
        return hash(self.id)