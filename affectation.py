# ============================================================
# affectation.py — Affectation des salles après coloration
# Projet : Planification d'Examens par Coloration de Graphes
# L2 Informatique — Théorie des Graphes 2025-2026
# ============================================================

from donnees import UES, SALLES, SURVEILLANTS, INTERDICTIONS


class ResultatAffectation:
    """Stocke l'affectation finale : UE -> (créneau, salle)."""

    def __init__(self):
        # dict : code_ue -> {"creneau": int, "salle": str, "surveillant": str}
        self.affectation = {}
        self.violations = []

    def ajouter(self, code_ue, creneau, salle, surveillant):
        self.affectation[code_ue] = {
            "creneau": creneau,
            "salle": salle,
            "surveillant": surveillant
        }

    def ajouter_violation(self, msg):
        self.violations.append(msg)


def affecter_salles(graphe, resultat_coloration):
    """
    Affecte une salle à chaque UE après coloration.

    Règles :
    - Capacité salle >= nb_étudiants UE
    - UE besoin_labo=True => salle est_labo=True
    - Deux UE du même créneau ne peuvent pas avoir la même salle
    - Priorité aux UE à grand effectif (affectées en premier)

    Retourne un ResultatAffectation.
    """
    ues_dict = {ue["code"]: ue for ue in UES}
    salles = sorted(SALLES, key=lambda s: s["capacite"], reverse=True)
    couleurs = resultat_coloration.couleurs
    resultat = ResultatAffectation()

    # Regrouper les UE par créneau (couleur)
    creneaux_ues = {}
    for code, creneau in couleurs.items():
        creneaux_ues.setdefault(creneau, []).append(code)

    # Pour chaque créneau, trier les UE par effectif décroissant (contrainte souhaitée)
    for creneau in sorted(creneaux_ues.keys()):
        ues_du_creneau = sorted(
            creneaux_ues[creneau],
            key=lambda c: ues_dict[c]["nb_etudiants"],
            reverse=True
        )

        salles_prises = set()  # salles déjà assignées pour ce créneau

        for code in ues_du_creneau:
            ue = ues_dict[code]
            surveillant = SURVEILLANTS.get(code, "—")
            salle_choisie = None

            for salle in salles:
                # Vérification capacité
                if salle["capacite"] < ue["nb_etudiants"]:
                    continue
                # Vérification type salle
                if ue["besoin_labo"] and not salle["est_labo"]:
                    continue
                # Vérification disponibilité
                if salle["code"] in salles_prises:
                    continue
                salle_choisie = salle
                break

            if salle_choisie:
                salles_prises.add(salle_choisie["code"])
                resultat.ajouter(code, creneau, salle_choisie["code"], surveillant)
            else:
                # Aucune salle disponible — violation à signaler
                resultat.ajouter_violation(
                    f"⚠️  {code} ({ue['nom']}) : aucune salle disponible au créneau {creneau + 1} "
                    f"(besoin: cap≥{ue['nb_etudiants']}, labo={ue['besoin_labo']})"
                )
                # Affecter quand même (sans salle)
                resultat.ajouter(code, creneau, "???", surveillant)

    return resultat


def auditer_planning(graphe, resultat_coloration, resultat_affectation):
    """
    Vérifie toutes les contraintes obligatoires et souhaitées.
    Retourne un rapport détaillé sous forme de chaîne.
    """
    ues_dict = {ue["code"]: ue for ue in UES}
    couleurs = resultat_coloration.couleurs
    affectation = resultat_affectation.affectation

    rapport = []
    nb_ok = 0
    nb_ko = 0

    rapport.append("=" * 64)
    rapport.append("  RAPPORT D'AUDIT — CONTRAINTES OBLIGATOIRES")
    rapport.append("=" * 64)

    # ---- 1. Étudiants en commun -> créneaux différents ----
    rapport.append("\n  [1] Étudiants en commun → créneaux différents")
    ok_tous = True
    for code_a in graphe.codes:
        for code_b in graphe.voisins(code_a):
            if code_a >= code_b:
                continue
            if couleurs.get(code_a) == couleurs.get(code_b):
                rapport.append(f"    ❌ {code_a} et {code_b} ont le même créneau !")
                nb_ko += 1
                ok_tous = False
    if ok_tous:
        rapport.append("    ✅ Aucun conflit étudiant détecté.")
        nb_ok += 1

    # ---- 2. Salle utilisée une fois par créneau ----
    rapport.append("\n  [2] Salle unique par créneau")
    ok_tous = True
    creneaux_salles = {}
    for code, info in affectation.items():
        cle = (info["creneau"], info["salle"])
        if info["salle"] == "???":
            continue
        if cle in creneaux_salles:
            rapport.append(f"    ❌ Salle {info['salle']} utilisée 2x au créneau {info['creneau']+1} : "
                           f"{creneaux_salles[cle]} et {code}")
            nb_ko += 1
            ok_tous = False
        else:
            creneaux_salles[cle] = code
    if ok_tous:
        rapport.append("    ✅ Chaque salle est utilisée au plus une fois par créneau.")
        nb_ok += 1

    # ---- 3. Capacité des salles ----
    rapport.append("\n  [3] Capacité des salles respectée")
    salles_dict = {s["code"]: s for s in SALLES}
    ok_tous = True
    for code, info in affectation.items():
        if info["salle"] == "???":
            continue
        salle = salles_dict.get(info["salle"])
        ue = ues_dict[code]
        if salle and salle["capacite"] < ue["nb_etudiants"]:
            rapport.append(f"    ❌ {code} : {ue['nb_etudiants']} étudiants > capacité {salle['capacite']} "
                           f"(salle {info['salle']})")
            nb_ko += 1
            ok_tous = False
    if ok_tous:
        rapport.append("    ✅ Toutes les capacités sont respectées.")
        nb_ok += 1

    # ---- 4. Surveillant pas dans 2 salles simultanément ----
    rapport.append("\n  [4] Surveillant unique par créneau")
    ok_tous = True
    creneaux_surv = {}
    for code, info in affectation.items():
        surv = info["surveillant"]
        creneau = info["creneau"]
        if surv == "—":
            continue
        cle = (creneau, surv)
        if cle in creneaux_surv:
            rapport.append(f"    ❌ {surv} surveille 2 UE au créneau {creneau+1} : "
                           f"{creneaux_surv[cle]} et {code}")
            nb_ko += 1
            ok_tous = False
        else:
            creneaux_surv[cle] = code
    if ok_tous:
        rapport.append("    ✅ Aucun surveillant en double par créneau.")
        nb_ok += 1

    # ---- 5. Labo pour UE besoin_labo ----
    rapport.append("\n  [5] Type de salle (labo si requis)")
    ok_tous = True
    for code, info in affectation.items():
        if info["salle"] == "???":
            continue
        ue = ues_dict[code]
        salle = salles_dict.get(info["salle"])
        if ue["besoin_labo"] and salle and not salle["est_labo"]:
            rapport.append(f"    ❌ {code} nécessite un labo mais est en salle standard {info['salle']}")
            nb_ko += 1
            ok_tous = False
    if ok_tous:
        rapport.append("    ✅ Toutes les UE labo sont bien en laboratoire.")
        nb_ok += 1

    # ---- Contraintes souhaitées ----
    rapport.append("\n" + "=" * 64)
    rapport.append("  CONTRAINTES SOUHAITÉES")
    rapport.append("=" * 64)

    # Espacement entre examens d'une même filière
    rapport.append("\n  [6] Espacement entre examens d'une même filière")
    filieres = {}
    for code, info in affectation.items():
        filiere = ues_dict[code]["filiere"]
        filieres.setdefault(filiere, []).append(info["creneau"])

    ok_tous = True
    for filiere, crens in filieres.items():
        crens_tries = sorted(crens)
        for i in range(len(crens_tries) - 1):
            if crens_tries[i+1] - crens_tries[i] < 2:
                rapport.append(f"    ⚠️  Filière {filiere} : créneaux {crens_tries[i]+1} "
                                f"et {crens_tries[i+1]+1} consécutifs.")
                ok_tous = False
    if ok_tous:
        rapport.append("    ✅ Au moins un créneau libre entre chaque examen d'une même filière.")

    # Interdictions explicites
    rapport.append("\n  [7] Interdictions explicites entre paires d'UE")
    ok_tous = True
    for code_a, code_b in INTERDICTIONS:
        info_a = affectation.get(code_a)
        info_b = affectation.get(code_b)
        if info_a and info_b:
            # Même jour = même créneau // 4 (4 créneaux par jour)
            jour_a = info_a["creneau"] // 4
            jour_b = info_b["creneau"] // 4
            if jour_a == jour_b:
                rapport.append(f"    ❌ {code_a} et {code_b} ont lieu le même jour (jour {jour_a+1})")
                ok_tous = False
    if ok_tous:
        rapport.append("    ✅ Toutes les interdictions explicites sont respectées.")

    # Résumé
    rapport.append("\n" + "=" * 64)
    rapport.append(f"  RÉSUMÉ : {nb_ok} contraintes OK | {nb_ko} violations")
    rapport.append("=" * 64)

    # Violations de l'affectation (salles manquantes)
    if resultat_affectation.violations:
        rapport.append("\n  ⚠️  VIOLATIONS D'AFFECTATION DE SALLES :")
        for v in resultat_affectation.violations:
            rapport.append(f"    {v}")

    return "\n".join(rapport)
