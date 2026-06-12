# ============================================================
# planning.py — Export CSV du planning + rapport PDF
# Projet : Planification d'Examens par Coloration de Graphes
# L2 Informatique — Théorie des Graphes 2025-2026
# ============================================================

import csv
import os
from donnees import UES, SALLES, NB_JOURS, NB_CRENEAUX_PAR_JOUR


# ============================================================
# Export CSV
# ============================================================

def exporter_csv(resultat_affectation, chemin="planning.csv"):
    """
    Génère un fichier CSV au format créneau × salle.
    Chaque cellule contient : CODE_UE (N étudiants)
    """
    ues_dict = {ue["code"]: ue for ue in UES}
    salles = [s["code"] for s in SALLES]
    nb_creneaux = NB_JOURS * NB_CRENEAUX_PAR_JOUR

    # Construire la grille créneau x salle
    grille = {}
    for code, info in resultat_affectation.affectation.items():
        creneau = info["creneau"]
        salle = info["salle"]
        ue = ues_dict[code]
        grille[(creneau, salle)] = f"{code} ({ue['nb_etudiants']} étudiants)"

    with open(chemin, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")

        # En-tête
        entete = ["Créneau / Salle"] + salles
        writer.writerow(entete)

        # Lignes
        for c in range(nb_creneaux):
            jour = c // NB_CRENEAUX_PAR_JOUR + 1
            slot = c % NB_CRENEAUX_PAR_JOUR + 1
            label_creneau = f"Jour {jour} - Créneau {slot}"
            ligne = [label_creneau]
            for salle in salles:
                cellule = grille.get((c, salle), "")
                ligne.append(cellule)
            writer.writerow(ligne)

    print(f"  ✅ Planning CSV exporté : {chemin}")
    return chemin


# ============================================================
# Rapport PDF avec ReportLab
# ============================================================

def generer_rapport_pdf(graphe, res_wp, res_ds, res_affectation,
                        audit_str, chemin_graphe_png,
                        chemin_sortie="rapport_coloration.pdf"):
    """
    Génère un rapport PDF complet (5-9 pages) décrivant :
    - La modélisation du graphe
    - Les algorithmes utilisés
    - Les résultats et analyse critique
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        PageBreak, Image, HRFlowable
    )
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT

    ues_dict = {ue["code"]: ue for ue in UES}

    doc = SimpleDocTemplate(
        chemin_sortie,
        pagesize=A4,
        leftMargin=2.5*cm, rightMargin=2.5*cm,
        topMargin=2.5*cm, bottomMargin=2.5*cm
    )
    styles = getSampleStyleSheet()

    # Styles personnalisés
    titre_style = ParagraphStyle(
        "TitrePrincipal",
        parent=styles["Title"],
        fontSize=20,
        textColor=colors.HexColor("#1a1a2e"),
        spaceAfter=6,
        alignment=TA_CENTER
    )
    sous_titre_style = ParagraphStyle(
        "SousTitre",
        parent=styles["Normal"],
        fontSize=12,
        textColor=colors.HexColor("#2c3e50"),
        alignment=TA_CENTER,
        spaceAfter=4
    )
    h1_style = ParagraphStyle(
        "H1",
        parent=styles["Heading1"],
        fontSize=14,
        textColor=colors.HexColor("#1a1a2e"),
        borderPad=4,
        spaceBefore=18,
        spaceAfter=8
    )
    h2_style = ParagraphStyle(
        "H2",
        parent=styles["Heading2"],
        fontSize=12,
        textColor=colors.HexColor("#2c3e50"),
        spaceBefore=12,
        spaceAfter=6
    )
    corps_style = ParagraphStyle(
        "Corps",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        alignment=TA_JUSTIFY
    )
    code_style = ParagraphStyle(
        "Code",
        parent=styles["Code"],
        fontSize=8,
        backColor=colors.HexColor("#f5f5f5"),
        leftIndent=12,
        rightIndent=12
    )

    story = []

    # =========================================================
    # PAGE DE GARDE
    # =========================================================
    story.append(Spacer(1, 3*cm))
    story.append(Paragraph("RAPPORT DE PROJET", titre_style))
    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(width="80%", thickness=2,
                             color=colors.HexColor("#E74C3C"), hAlign="CENTER"))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(
        "Planification d'Examens par Coloration de Graphes",
        ParagraphStyle("GrandTitre", parent=titre_style, fontSize=16)
    ))
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph("L2 Informatique — Théorie des Graphes", sous_titre_style))
    story.append(Paragraph("Année universitaire 2025-2026", sous_titre_style))
    story.append(Spacer(1, 4*cm))

    infos = [
        ["Module :", "Théorie des Graphes"],
        ["Niveau :", "L2 Informatique"],
        ["Algorithmes :", "Welsh-Powell & DSATUR"],
        ["Langage :", "Python 3"],
        ["Librairies :", "networkx, matplotlib, reportlab"],
    ]
    t = Table(infos, colWidths=[4*cm, 10*cm])
    t.setStyle(TableStyle([
        ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 10),
        ("TEXTCOLOR", (0,0), (0,-1), colors.HexColor("#E74C3C")),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]))
    story.append(t)
    story.append(PageBreak())

    # =========================================================
    # PARTIE 1 — MODÉLISATION
    # =========================================================
    story.append(Paragraph("I. Modélisation du Problème", h1_style))
    story.append(HRFlowable(width="100%", thickness=1,
                             color=colors.HexColor("#bdc3c7")))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("1.1 Contexte et objectif", h2_style))
    story.append(Paragraph(
        "Le problème de planification d'examens consiste à affecter un créneau horaire "
        "et une salle à chaque Unité d'Enseignement (UE), en évitant tout conflit entre "
        "UE qui partagent des étudiants, des surveillants, ou qui font l'objet "
        "d'interdictions explicites. Ce problème se ramène naturellement à un "
        "<b>problème de coloration de graphe</b>.", corps_style
    ))

    story.append(Paragraph("1.2 Définition formelle du graphe", h2_style))
    story.append(Paragraph(
        "Soit G = (V, E) le graphe de conflits défini comme suit :", corps_style
    ))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        "• <b>V</b> : ensemble des UE (chaque UE est un sommet)", corps_style
    ))
    story.append(Paragraph(
        "• <b>E</b> : arête (u, v) si et seulement si les UE u et v partagent "
        "au moins un étudiant, ou ont le même surveillant, ou font l'objet d'une "
        "interdiction explicite.", corps_style
    ))
    story.append(Paragraph(
        "• Une <b>coloration valide</b> assigne à chaque sommet une couleur (créneau) "
        "telle qu'aucun deux sommets adjacents n'aient la même couleur.", corps_style
    ))

    story.append(Paragraph("1.3 Statistiques du graphe", h2_style))
    stats_data = [
        ["Propriété", "Valeur"],
        ["Nombre de sommets (UE)", str(graphe.nb_sommets())],
        ["Nombre d'arêtes (conflits)", str(graphe.nb_aretes())],
        ["Degré maximum", str(max(graphe.degre(c) for c in graphe.codes))],
        ["Degré minimum", str(min(graphe.degre(c) for c in graphe.codes))],
        ["Degré moyen", f"{sum(graphe.degre(c) for c in graphe.codes)/graphe.nb_sommets():.2f}"],
    ]
    t = Table(stats_data, colWidths=[9*cm, 6*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1a1a2e")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 10),
        ("ROWBACKGROUNDS", (0,1), (-1,-1),
         [colors.HexColor("#f8f9fa"), colors.HexColor("#ecf0f1")]),
        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#bdc3c7")),
        ("ALIGN", (1,0), (1,-1), "CENTER"),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING", (0,0), (-1,-1), 6),
    ]))
    story.append(t)

    story.append(Paragraph("1.4 Degrés des sommets", h2_style))
    deg_data = [["UE", "Nom", "Filière", "Étudiants", "Degré"]]
    for code in sorted(graphe.codes, key=lambda c: graphe.degre(c), reverse=True):
        ue = ues_dict[code]
        deg_data.append([
            code, ue["nom"], ue["filiere"],
            str(ue["nb_etudiants"]), str(graphe.degre(code))
        ])
    t = Table(deg_data, colWidths=[2.5*cm, 5.5*cm, 2*cm, 2.5*cm, 2*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#2c3e50")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS", (0,1), (-1,-1),
         [colors.white, colors.HexColor("#f8f9fa")]),
        ("GRID", (0,0), (-1,-1), 0.3, colors.HexColor("#bdc3c7")),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("TOPPADDING", (0,0), (-1,-1), 4),
    ]))
    story.append(t)
    story.append(PageBreak())

    # =========================================================
    # PARTIE 2 — ALGORITHMES
    # =========================================================
    story.append(Paragraph("II. Algorithmes de Coloration", h1_style))
    story.append(HRFlowable(width="100%", thickness=1,
                             color=colors.HexColor("#bdc3c7")))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("2.1 Welsh-Powell", h2_style))
    story.append(Paragraph(
        "L'algorithme Welsh-Powell est un algorithme glouton qui procède en deux étapes :", corps_style
    ))
    story.append(Paragraph(
        "<b>Étape 1</b> — Trier tous les sommets par degré décroissant. "
        "Les sommets les plus connectés (ayant le plus de conflits) sont traités en premier.", corps_style
    ))
    story.append(Paragraph(
        "<b>Étape 2</b> — Parcourir les sommets dans cet ordre et attribuer à chacun "
        "le plus petit numéro de créneau non utilisé par ses voisins déjà colorés.", corps_style
    ))
    story.append(Paragraph(
        "Complexité temporelle : O(n<super>2</super> + m), "
        "où n est le nombre de sommets et m le nombre d'arêtes.", corps_style
    ))

    story.append(Paragraph("2.2 DSATUR (Degree of SATURation)", h2_style))
    story.append(Paragraph(
        "DSATUR, proposé par Brélaz (1979), est un algorithme glouton amélioré. "
        "Plutôt que de suivre un ordre fixe, il choisit dynamiquement à chaque étape "
        "le sommet non coloré avec le plus grand <b>degré de saturation</b> "
        "(nombre de couleurs/créneaux distincts dans son voisinage immédiat). "
        "En cas d'égalité, le sommet de plus grand degré est choisi.", corps_style
    ))
    story.append(Paragraph(
        "Cette approche adaptative permet souvent d'obtenir une coloration avec "
        "moins de couleurs que Welsh-Powell, en particulier sur des graphes denses.", corps_style
    ))

    story.append(Paragraph("2.3 Comparaison des résultats", h2_style))
    comp_data = [
        ["Critère", "Welsh-Powell", "DSATUR"],
        ["Créneaux utilisés",
         str(res_wp.nb_couleurs),
         str(res_ds.nb_couleurs)],
        ["Temps d'exécution",
         f"{res_wp.temps_ms:.4f} ms",
         f"{res_ds.temps_ms:.4f} ms"],
        ["Stratégie de tri",
         "Ordre fixe (degrés décroissants)",
         "Ordre dynamique (saturation)"],
        ["Optimalité",
         "Pas garantie",
         "Meilleure en pratique"],
    ]
    t = Table(comp_data, colWidths=[5*cm, 5.5*cm, 5.5*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#E74C3C")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS", (0,1), (-1,-1),
         [colors.white, colors.HexColor("#fef9f9")]),
        ("GRID", (0,0), (-1,-1), 0.3, colors.HexColor("#bdc3c7")),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
    ]))
    story.append(t)

    story.append(Paragraph("2.4 Analyse critique", h2_style))
    if res_ds.nb_couleurs <= res_wp.nb_couleurs:
        meilleur = "DSATUR"
        raison = ("grâce à son choix adaptatif du prochain sommet à colorier, "
                  "basé sur la saturation courante du voisinage")
    else:
        meilleur = "Welsh-Powell"
        raison = ("car le tri initial par degré décroissant capture bien la structure "
                  "de conflits de ce graphe particulier")
    story.append(Paragraph(
        f"Sur notre jeu de données, <b>{meilleur}</b> obtient le meilleur résultat, "
        f"{raison}. "
        "Notons que ni l'un ni l'autre ne garantit la coloration optimale "
        "(nombre chromatique exact χ(G)), car le problème de coloration est NP-difficile. "
        "Cependant, ces heuristiques offrent un excellent rapport qualité/rapidité "
        "pour des instances pratiques.", corps_style
    ))
    story.append(PageBreak())

    # =========================================================
    # PARTIE 3 — PLANNING FINAL
    # =========================================================
    story.append(Paragraph("III. Planning Final et Affectation des Salles", h1_style))
    story.append(HRFlowable(width="100%", thickness=1,
                             color=colors.HexColor("#bdc3c7")))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("3.1 Planning détaillé (algorithme DSATUR)", h2_style))

    # Trier par créneau
    planning_data = [["Créneau", "UE", "Nom de l'UE", "Salle", "Effectif", "Surveillant"]]
    for code, info in sorted(
        res_affectation.affectation.items(),
        key=lambda x: (x[1]["creneau"], x[0])
    ):
        ue = ues_dict[code]
        jour = info["creneau"] // NB_CRENEAUX_PAR_JOUR + 1
        slot = info["creneau"] % NB_CRENEAUX_PAR_JOUR + 1
        label = f"J{jour} - C{slot}"
        planning_data.append([
            label, code, ue["nom"], info["salle"],
            str(ue["nb_etudiants"]), info["surveillant"]
        ])

    t = Table(planning_data, colWidths=[1.8*cm, 2*cm, 4.5*cm, 2*cm, 2*cm, 3.5*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#2c3e50")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 8),
        ("ROWBACKGROUNDS", (0,1), (-1,-1),
         [colors.white, colors.HexColor("#f0f3f4")]),
        ("GRID", (0,0), (-1,-1), 0.3, colors.HexColor("#bdc3c7")),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("ALIGN", (2,0), (2,-1), "LEFT"),
    ]))
    story.append(t)

    # Graphe coloré
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("3.2 Visualisation du graphe coloré", h2_style))
    if os.path.exists(chemin_graphe_png):
        img = Image(chemin_graphe_png, width=14*cm, height=9*cm)
        story.append(img)
        story.append(Paragraph(
            "Figure 1 — Graphe de conflits coloré par DSATUR. "
            "Chaque couleur correspond à un créneau horaire distinct.",
            ParagraphStyle("Caption", parent=styles["Normal"],
                           fontSize=8, alignment=TA_CENTER,
                           textColor=colors.gray)
        ))
    story.append(PageBreak())

    # =========================================================
    # AUDIT
    # =========================================================
    story.append(Paragraph("IV. Rapport d'Audit des Contraintes", h1_style))
    story.append(HRFlowable(width="100%", thickness=1,
                             color=colors.HexColor("#bdc3c7")))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "Le rapport d'audit ci-dessous vérifie le respect de toutes les contraintes "
        "obligatoires et souhaitées définies dans le cahier des charges.", corps_style
    ))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        audit_str.replace("\n", "<br/>"),
        ParagraphStyle("Audit", parent=styles["Code"],
                       fontSize=8, leading=12,
                       backColor=colors.HexColor("#f8f9fa"),
                       leftIndent=8, rightIndent=8,
                       borderPad=8)
    ))

    story.append(PageBreak())

    # =========================================================
    # CONCLUSION
    # =========================================================
    story.append(Paragraph("V. Conclusion", h1_style))
    story.append(HRFlowable(width="100%", thickness=1,
                             color=colors.HexColor("#bdc3c7")))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "Ce projet nous a permis d'appliquer la théorie des graphes à un problème "
        "concret de planification. La modélisation par graphe de conflits est "
        "naturelle et efficace : chaque source de conflit (étudiants partagés, "
        "surveillants, interdictions) se traduit directement en arête.", corps_style
    ))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "Les algorithmes Welsh-Powell et DSATUR, bien que non optimaux en théorie, "
        "donnent des résultats satisfaisants en temps polynomial. DSATUR, grâce à "
        "son choix adaptatif, tend à mieux exploiter la structure locale du graphe.", corps_style
    ))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "Des pistes d'amélioration existent : recuit simulé, algorithmes génétiques "
        "(partie bonus du CDC), ou encore l'utilisation de solveurs SAT qui peuvent "
        "trouver la coloration optimale (nombre chromatique exact) pour des instances "
        "de taille raisonnable.", corps_style
    ))

    # Construction du document
    doc.build(story)
    print(f"  ✅ Rapport PDF généré : {chemin_sortie}")
    return chemin_sortie
