import csv
import os
from typing import Dict, List, Tuple

from .models import Creneau, Room, Student, UE

DEFAULT_INPUT_DIR = os.path.join(os.path.dirname(__file__), "input")


def _read_csv(path: str) -> List[Dict[str, str]]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_creneaux(input_dir: str = DEFAULT_INPUT_DIR) -> List[Creneau]:
    rows = _read_csv(os.path.join(input_dir, "creneaux.csv"))
    return [
        Creneau(
            id=row["ID"].strip(),
            jour=row["Jour"].strip(),
            plage=row["Plage_Horaire"].strip(),
        )
        for row in rows
    ]


def load_rooms(input_dir: str = DEFAULT_INPUT_DIR) -> List[Room]:
    rows = _read_csv(os.path.join(input_dir, "rooms.csv"))
    rooms = []
    for row in rows:
        room_type = row.get("type", "standard").strip().lower()
        rooms.append(
            Room(
                id=row["nom"].strip(),
                capacity=int(row["capacite"].strip()),
                is_lab=room_type in ("labo", "lab", "laboratoire"),
            )
        )
    return rooms


def load_surveillants(input_dir: str = DEFAULT_INPUT_DIR) -> Dict[str, str]:
    path = os.path.join(input_dir, "surveillants.csv")
    if not os.path.exists(path):
        return {}
    return {
        row["Code_UE"].strip(): row["Surveillant"].strip()
        for row in _read_csv(path)
    }


def load_ues(input_dir: str = DEFAULT_INPUT_DIR) -> List[UE]:
    surveillants = load_surveillants(input_dir)
    rows = _read_csv(os.path.join(input_dir, "ues.csv"))
    ues = []
    for row in rows:
        code = row["Code"].strip()
        besoin_labo = row.get("Besoin_Labo", "Non").strip().lower()
        ues.append(
            UE(
                id=code,
                name=row["Nom"].strip(),
                filiere=row["Filiere"].strip(),
                is_lab=besoin_labo in ("oui", "yes", "1", "true"),
                surveillant=surveillants.get(code, ""),
            )
        )
    return ues


def load_students(
    ues: List[UE], input_dir: str = DEFAULT_INPUT_DIR
) -> List[Student]:
    """Inscrit chaque étudiant à toutes les UEs de sa filière."""
    ue_by_filiere: Dict[str, List[str]] = {}
    for ue in ues:
        ue_by_filiere.setdefault(ue.filiere, []).append(ue.id)

    ue_dict = {ue.id: ue for ue in ues}
    students = []

    for row in _read_csv(os.path.join(input_dir, "etudiants.csv")):
        student_id = row["ID"].strip()
        filiere = row["Filiere"].strip()
        enrolled = ue_by_filiere.get(filiere, [])

        student = Student(
            id=student_id,
            name=row["Nom"].strip(),
            filiere=filiere,
            ues=set(enrolled),
        )
        students.append(student)

        for ue_id in enrolled:
            ue_dict[ue_id].students.add(student_id)

    return students


def load_data(
    input_dir: str = DEFAULT_INPUT_DIR,
) -> Tuple[List[UE], List[Room], List[Student], List[Creneau]]:
    """Charge l'ensemble des données réelles depuis Data/input/."""
    ues = load_ues(input_dir)
    rooms = load_rooms(input_dir)
    students = load_students(ues, input_dir)
    creneaux = load_creneaux(input_dir)
    return ues, rooms, students, creneaux
