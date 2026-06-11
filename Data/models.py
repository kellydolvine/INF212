from dataclasses import dataclass, field
from typing import Set


@dataclass
class UE:
    """Représente une Unité d'Enseignement (UE)."""
    id: str
    name: str
    filiere: str = ""
    students: Set[str] = field(default_factory=set)
    is_lab: bool = False
    surveillant: str = ""

    @property
    def student_count(self) -> int:
        return len(self.students)


@dataclass
class Room:
    """Représente une salle d'examen."""
    id: str
    capacity: int
    is_lab: bool = False


@dataclass
class Student:
    """Représente un étudiant."""
    id: str
    name: str
    filiere: str = ""
    ues: Set[str] = field(default_factory=set)


@dataclass
class Creneau:
    """Représente un créneau horaire disponible pour les examens."""
    id: str
    jour: str
    plage: str

    @property
    def label(self) -> str:
        return f"{self.jour} {self.plage}"
