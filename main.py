#!/usr/bin/env python3
# ============================================================
# main.py — Point d'entrée du projet
# Projet : Planification d'Examens par Coloration de Graphes
# L2 Informatique — Théorie des Graphes 2025-2026
# ============================================================

import os
import sys

# Répertoire de sortie
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

def main():
    print("\n" + "█"*62)
    print("  PLANIFICATION D'EXAMENS PAR COLORATION DE GRAPHES")
    print("  L2 Informatique — Théorie des Graphes 2025-2026")
    print("█"*62)

    # ==================================================
    # PARTIE 1 — Construction du graphe de conflits
    # ==================================================
    print("\n\n📌 PARTIE 1 — Construction du graphe de conflits")
    print("-"*55)

    from graphe import GrapheConflits
    g = GrapheConflits()
    g.afficher_statistiques()

    # Visualisation sans coloration
    chemin_graphe_base = os.path.join(OUTPUT_DIR, "graphe_base.png")
    g.visualiser(couleurs=None, chemin_sortie=chemin_graphe_base)

    # ==================================================
    # PARTIE 2 — Algorithmes de coloration
    # ==================================================
    print("\n\n📌 PARTIE 2 — Algorithmes de coloration")
    print("-"*55)

    from coloration import welsh_powell, dsatur, comparer_algorithmes, verifier_coloration

    # Exécution et affichage des deux algorithmes
    res_wp = welsh_powell(g)
    res_wp.afficher()

    res_ds = dsatur(g)
    res_ds.afficher()

    # Comparaison
    res_wp, res_ds = comparer_algorithmes(g, nb_repetitions=500)

    # Vérification de validité
    print("\n  Vérification des colorations :")
    valide_wp, conflits_wp = verifier_coloration(g, res_wp)
    valide_ds, conflits_ds = verifier_coloration(g, res_ds)
    print(f"  Welsh-Powell : {'✅ valide' if valide_wp else '❌ invalide — ' + str(conflits_wp)}")
    print(f"  DSATUR       : {'✅ valide' if valide_ds else '❌ invalide — ' + str(conflits_ds)}")

    # Visualisation avec coloration (on utilise DSATUR comme résultat final)
    chemin_graphe_color = os.path.join(OUTPUT_DIR, "graphe_colore.png")
    g.visualiser(couleurs=res_ds.couleurs, chemin_sortie=chemin_graphe_color)

    # ==================================================
    # PARTIE 3 — Affectation des salles + planning
    # ==================================================
    print("\n\n📌 PARTIE 3 — Affectation des salles et planning final")
    print("-"*55)

    from affectation import affecter_salles, auditer_planning
    from planning import exporter_csv, generer_rapport_pdf

    # Affectation des salles (basée sur DSATUR)
    res_affectation = affecter_salles(g, res_ds)

    # Audit
    print("\n  Génération du rapport d'audit...")
    audit = auditer_planning(g, res_ds, res_affectation)
    print(audit)

    # Export CSV
    print()
    chemin_csv = os.path.join(OUTPUT_DIR, "planning.csv")
    exporter_csv(res_affectation, chemin=chemin_csv)

    # Rapport PDF
    chemin_pdf = os.path.join(OUTPUT_DIR, "rapport_coloration.pdf")
    generer_rapport_pdf(
        g, res_wp, res_ds, res_affectation,
        audit,
        chemin_graphe_color,
        chemin_sortie=chemin_pdf
    )

    # ==================================================
    # RÉCAPITULATIF DES FICHIERS GÉNÉRÉS
    # ==================================================
    print("\n\n" + "="*62)
    print("  FICHIERS GÉNÉRÉS")
    print("="*62)
    fichiers = [
        ("graphe_base.png",       "Graphe sans coloration"),
        ("graphe_colore.png",     "Graphe coloré (DSATUR)"),
        ("planning.csv",          "Planning créneau × salle"),
        ("rapport_coloration.pdf","Rapport PDF complet"),
    ]
    for nom, desc in fichiers:
        chemin = os.path.join(OUTPUT_DIR, nom)
        existe = "✅" if os.path.exists(chemin) else "❌"
        print(f"  {existe}  {nom:<30} {desc}")
    print("="*62 + "\n")


if __name__ == "__main__":
    main()
