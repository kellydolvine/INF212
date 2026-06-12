# ============================================================
# donnees.py — Jeu de données de test pour le projet
# Projet : Planification d'Examens par Coloration de Graphes
# L2 Informatique — Théorie des Graphes 2025-2026
# ============================================================

# --- Unités d'Enseignement ---
# Chaque UE : {code, nom, filiere, nb_etudiants, besoin_labo}
UES = [
    {"code": "INF201", "nom": "Algorithmique",         "filiere": "INFO", "nb_etudiants": 45, "besoin_labo": False},
    {"code": "INF202", "nom": "Bases de Données",       "filiere": "INFO", "nb_etudiants": 40, "besoin_labo": True},
    {"code": "INF203", "nom": "Réseaux",                "filiere": "INFO", "nb_etudiants": 38, "besoin_labo": False},
    {"code": "INF204", "nom": "Systèmes d'Exploitation","filiere": "INFO", "nb_etudiants": 42, "besoin_labo": False},
    {"code": "INF205", "nom": "Programmation Web",      "filiere": "INFO", "nb_etudiants": 50, "besoin_labo": True},
    {"code": "MAT201", "nom": "Analyse",                "filiere": "MATH", "nb_etudiants": 60, "besoin_labo": False},
    {"code": "MAT202", "nom": "Algèbre",                "filiere": "MATH", "nb_etudiants": 55, "besoin_labo": False},
    {"code": "MAT203", "nom": "Probabilités",           "filiere": "MATH", "nb_etudiants": 48, "besoin_labo": False},
    {"code": "PHY201", "nom": "Électromagnétisme",      "filiere": "PHYS", "nb_etudiants": 35, "besoin_labo": False},
    {"code": "PHY202", "nom": "Mécanique Quantique",    "filiere": "PHYS", "nb_etudiants": 30, "besoin_labo": False},
    {"code": "INF206", "nom": "Intelligence Artificielle","filiere": "INFO","nb_etudiants": 44, "besoin_labo": True},
    {"code": "INF207", "nom": "Théorie des Graphes",    "filiere": "INFO", "nb_etudiants": 41, "besoin_labo": False},
]

# --- Inscriptions : liste de (code_UE, id_etudiant) ---
# Représente quels étudiants sont inscrits à quelles UE
INSCRIPTIONS = [
    # INF201 — Algorithmique
    ("INF201", *range(1, 46)),
    # INF202 — Bases de Données (partage étudiants avec INF201, INF204, INF207)
    ("INF202", *range(10, 51)),
    # INF203 — Réseaux (partage avec INF201, INF204)
    ("INF203", *range(5, 43)),
    # INF204 — Systèmes d'Exploitation (partage avec INF201, INF202, INF203)
    ("INF204", *range(1, 43)),
    # INF205 — Programmation Web (partage avec INF202, INF206)
    ("INF205", *range(20, 71)),
    # MAT201 — Analyse (partage avec MAT202, MAT203)
    ("MAT201", *range(100, 161)),
    # MAT202 — Algèbre (partage avec MAT201, MAT203)
    ("MAT202", *range(110, 166)),
    # MAT203 — Probabilités (partage avec MAT201, MAT202, INF201)
    ("MAT203", *range(100, 149)),
    # PHY201 — Électromagnétisme
    ("PHY201", *range(200, 236)),
    # PHY202 — Mécanique Quantique (partage avec PHY201)
    ("PHY202", *range(205, 236)),
    # INF206 — Intelligence Artificielle (partage avec INF202, INF205)
    ("INF206", *range(25, 70)),
    # INF207 — Théorie des Graphes (partage avec INF201, INF202, INF204)
    ("INF207", *range(1, 42)),
]

# Convertir en dict : code_UE -> set d'étudiants
def get_etudiants_par_ue():
    etudiants = {}
    for entry in INSCRIPTIONS:
        code = entry[0]
        ids = set(entry[1:])
        etudiants[code] = ids
    return etudiants

# --- Salles disponibles ---
# Chaque salle : {code, capacite, est_labo}
SALLES = [
    {"code": "A101", "capacite": 60, "est_labo": False},
    {"code": "A102", "capacite": 50, "est_labo": False},
    {"code": "B201", "capacite": 45, "est_labo": False},
    {"code": "B202", "capacite": 40, "est_labo": False},
    {"code": "LABO1","capacite": 50, "est_labo": True},
    {"code": "LABO2","capacite": 45, "est_labo": True},
    {"code": "C301", "capacite": 35, "est_labo": False},
    {"code": "C302", "capacite": 30, "est_labo": False},
]

# --- Surveillants par UE ---
SURVEILLANTS = {
    "INF201": "Prof_Dupont",
    "INF202": "Prof_Martin",
    "INF203": "Prof_Dupont",   # Conflit avec INF201 !
    "INF204": "Prof_Bernard",
    "INF205": "Prof_Martin",   # Conflit avec INF202 !
    "MAT201": "Prof_Leclerc",
    "MAT202": "Prof_Leclerc",  # Conflit avec MAT201 !
    "MAT203": "Prof_Rousseau",
    "PHY201": "Prof_Girard",
    "PHY202": "Prof_Girard",   # Conflit avec PHY201 !
    "INF206": "Prof_Bernard",  # Conflit avec INF204 !
    "INF207": "Prof_Rousseau",
}

# --- Interdictions explicites (paires d'UE pas le même jour) ---
INTERDICTIONS = [
    ("MAT201", "PHY201"),
    ("INF205", "INF206"),
]

# --- Créneaux disponibles : 4 par jour, sur N jours ---
NB_JOURS = 5
NB_CRENEAUX_PAR_JOUR = 4

def get_creneaux():
    creneaux = []
    for j in range(1, NB_JOURS + 1):
        for c in range(1, NB_CRENEAUX_PAR_JOUR + 1):
            creneaux.append(f"J{j}_C{c}")
    return creneaux
