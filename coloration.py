# ============================================================
# coloration.py — Algorithmes de coloration de graphe
# Projet : Planification d'Examens par Coloration de Graphes
# L2 Informatique — Théorie des Graphes 2025-2026
# ============================================================

import time


class ResultatColoration:
    """Encapsule le résultat d'une coloration."""

    def __init__(self, nom_algo, couleurs, nb_couleurs, temps_ms):
        self.nom_algo = nom_algo
        # couleurs : dict {code_ue -> int (numéro de créneau, 0-indexé)}
        self.couleurs = couleurs
        self.nb_couleurs = nb_couleurs
        self.temps_ms = temps_ms

    def afficher(self):
        print(f"\n  ╔══ Résultat : {self.nom_algo} ══")
        print(f"  ║  Créneaux utilisés : {self.nb_couleurs}")
        print(f"  ║  Temps d'exécution : {self.temps_ms:.4f} ms")
        print(f"  ╠{'═'*44}")
        print(f"  ║  {'UE':<10} {'Créneau':>10}")
        print(f"  ╠{'─'*24}")
        for code, creneau in sorted(self.couleurs.items(), key=lambda x: x[1]):
            print(f"  ║  {code:<10} Créneau {creneau + 1:>2}")
        print(f"  ╚{'═'*44}")


# ============================================================
# Algorithme 1 — Welsh-Powell
# ============================================================

def welsh_powell(graphe):
    """
    Algorithme Welsh-Powell :
    1. Trier les sommets par degré décroissant
    2. Parcourir les sommets dans cet ordre
    3. Attribuer le plus petit créneau disponible (non utilisé
       par un voisin déjà coloré)

    Complexité : O(n² + m)  où n = nb sommets, m = nb arêtes
    """
    debut = time.perf_counter()

    # 1. Tri par degré décroissant
    sommets_tries = sorted(
        graphe.codes,
        key=lambda c: graphe.degre(c),
        reverse=True
    )

    couleurs = {}  # code -> numéro de créneau

    for sommet in sommets_tries:
        # Créneaux déjà pris par les voisins
        creneaux_voisins = {
            couleurs[v] for v in graphe.voisins(sommet)
            if v in couleurs
        }

        # Trouver le plus petit créneau disponible
        creneau = 0
        while creneau in creneaux_voisins:
            creneau += 1

        couleurs[sommet] = creneau

    fin = time.perf_counter()
    nb_couleurs = max(couleurs.values()) + 1
    temps_ms = (fin - debut) * 1000

    return ResultatColoration("Welsh-Powell", couleurs, nb_couleurs, temps_ms)


# ============================================================
# Algorithme 2 — DSATUR (Degree of SATURation)
# ============================================================

def dsatur(graphe):
    """
    Algorithme DSATUR (Brélaz, 1979) :
    À chaque étape, choisir le sommet non coloré avec le plus
    grand degré de saturation (= nombre de couleurs distinctes
    dans son voisinage). En cas d'égalité, prendre celui de
    plus grand degré dans le graphe original.

    Généralement meilleur que Welsh-Powell en pratique.
    Complexité : O(n² + m)
    """
    debut = time.perf_counter()

    couleurs = {}                        # code -> numéro de créneau
    saturation = {c: 0 for c in graphe.codes}   # nb couleurs distinctes chez voisins
    couleurs_voisins = {c: set() for c in graphe.codes}  # couleurs vues par chaque sommet

    non_colories = set(graphe.codes)

    while non_colories:
        # Choisir le sommet avec la plus grande saturation
        # (ex-aequo : plus grand degré original)
        sommet = max(
            non_colories,
            key=lambda c: (saturation[c], graphe.degre(c))
        )

        # Plus petit créneau disponible
        creneau = 0
        while creneau in couleurs_voisins[sommet]:
            creneau += 1

        couleurs[sommet] = creneau
        non_colories.remove(sommet)

        # Mettre à jour la saturation des voisins non colorés
        for voisin in graphe.voisins(sommet):
            if voisin in non_colories:
                avant = len(couleurs_voisins[voisin])
                couleurs_voisins[voisin].add(creneau)
                apres = len(couleurs_voisins[voisin])
                if apres > avant:
                    saturation[voisin] = apres

    fin = time.perf_counter()
    nb_couleurs = max(couleurs.values()) + 1
    temps_ms = (fin - debut) * 1000

    return ResultatColoration("DSATUR", couleurs, nb_couleurs, temps_ms)


# ============================================================
# Comparaison des deux algorithmes
# ============================================================

def comparer_algorithmes(graphe, nb_repetitions=1000):
    """
    Compare Welsh-Powell et DSATUR sur le même graphe.
    Exécute nb_repetitions fois chaque algo pour une mesure
    de temps fiable.
    """
    print("\n" + "="*60)
    print("  COMPARAISON DES ALGORITHMES DE COLORATION")
    print("="*60)

    # Mesure sur plusieurs répétitions
    temps_wp = []
    temps_ds = []
    for _ in range(nb_repetitions):
        t = time.perf_counter()
        welsh_powell(graphe)
        temps_wp.append((time.perf_counter() - t) * 1000)

        t = time.perf_counter()
        dsatur(graphe)
        temps_ds.append((time.perf_counter() - t) * 1000)

    res_wp = welsh_powell(graphe)
    res_ds = dsatur(graphe)

    moy_wp = sum(temps_wp) / len(temps_wp)
    moy_ds = sum(temps_ds) / len(temps_ds)

    print(f"\n  {'Critère':<35} {'Welsh-Powell':>13} {'DSATUR':>10}")
    print("  " + "-"*60)
    print(f"  {'Créneaux utilisés':<35} {res_wp.nb_couleurs:>13} {res_ds.nb_couleurs:>10}")
    print(f"  {'Temps moyen (ms) sur ' + str(nb_repetitions) + ' runs':<35} {moy_wp:>13.4f} {moy_ds:>10.4f}")
    print()

    # Analyse
    if res_wp.nb_couleurs < res_ds.nb_couleurs:
        print("  🏆 Welsh-Powell utilise moins de créneaux.")
    elif res_ds.nb_couleurs < res_wp.nb_couleurs:
        print("  🏆 DSATUR utilise moins de créneaux.")
    else:
        print("  ✅ Les deux algorithmes donnent le même nombre de créneaux.")

    if moy_wp < moy_ds:
        print("  ⚡ Welsh-Powell est plus rapide.")
    else:
        print("  ⚡ DSATUR est plus rapide.")

    print("="*60)
    return res_wp, res_ds


def verifier_coloration(graphe, resultat):
    """
    Vérifie qu'aucun sommet adjacent n'a la même couleur.
    Retourne (valide: bool, conflits: list)
    """
    conflits = []
    couleurs = resultat.couleurs

    for code_a in graphe.codes:
        for code_b in graphe.voisins(code_a):
            if code_a < code_b:
                if couleurs.get(code_a) == couleurs.get(code_b):
                    conflits.append((code_a, code_b, couleurs[code_a]))

    valide = len(conflits) == 0
    return valide, conflits
