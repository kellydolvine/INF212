from .models import UE, Room, Student
from typing import List, Tuple
import random

def generate_mock_data() -> Tuple[List[UE], List[Room], List[Student]]:
    """
    Génère un jeu de données réaliste pour tester l'application.
    
    Scénario : Un établissement avec 3 filières (Informatique, Maths/Sciences,
    Réseaux & Télécoms) doit planifier les examens de fin de semestre pour 8 UEs.
    
    Retourne :
        - ues : Liste des Unités d'Enseignement
        - rooms : Liste des salles disponibles
        - students : Liste des étudiants inscrits
    """
    random.seed(42)  # Résultats reproductibles
    
    # =========================================================================
    # 1. CRÉATION DES SALLES
    # =========================================================================
    rooms = [
        Room("Amphi A", 120, is_lab=False),
        Room("Amphi B", 100, is_lab=False),
        Room("Salle 101", 60, is_lab=False),
        Room("Salle 102", 50, is_lab=False),
        Room("Salle 103", 40, is_lab=False),
        Room("Salle 104", 35, is_lab=False),
        Room("Labo Info 1", 45, is_lab=True),
        Room("Labo Info 2", 35, is_lab=True),
    ]
    
    # =========================================================================
    # 2. CRÉATION DES UEs
    # =========================================================================
    ues = [
        UE("INF101", "Algorithmique 1", is_lab=False),
        UE("MAT101", "Analyse Mathématique", is_lab=False),
        UE("INF102", "Systèmes d'Exploitation", is_lab=False),
        UE("INF103", "Programmation C", is_lab=True),   # Nécessite un labo
        UE("MAT102", "Algèbre Linéaire", is_lab=False),
        UE("FIS101", "Physique Générale", is_lab=False),
        UE("ENG101", "Anglais Technique", is_lab=False),
        UE("INF104", "Réseaux Informatiques", is_lab=True),  # Nécessite un labo
    ]
    ue_dict = {ue.id: ue for ue in ues}
    
    # =========================================================================
    # 3. CRÉATION DES ÉTUDIANTS ET AFFECTATION AUX UEs
    # =========================================================================
    # 3 filières avec des UEs partagées (source des conflits dans le graphe)
    filieres = {
        "Informatique":       ["INF101", "MAT101", "INF102", "INF103", "ENG101"],
        "Maths & Sciences":   ["MAT101", "MAT102", "FIS101", "ENG101"],
        "Réseaux & Télécoms": ["INF101", "INF104", "FIS101", "ENG101"],
    }
    
    # Répartition : ~40 Info, ~30 Maths, ~30 Réseaux = 100 étudiants
    filiere_repartition = {
        "Informatique": 40,
        "Maths & Sciences": 30,
        "Réseaux & Télécoms": 30,
    }
    
    students = []
    student_id = 0
    
    for filiere_name, count in filiere_repartition.items():
        filiere_ues = filieres[filiere_name]
        for _ in range(count):
            s_id = f"STUD_{student_id:03d}"
            student_ues = set(filiere_ues)
            
            student = Student(s_id, f"Étudiant {student_id}", ues=student_ues)
            students.append(student)
            
            # Inscrire l'étudiant dans chaque UE de sa filière
            for ue_id in student_ues:
                ue_dict[ue_id].students.add(s_id)
                
            student_id += 1
    
    return ues, rooms, students
