# ============================================================
# graphe.py — Construction et visualisation du graphe de conflits
# Projet : Planification d'Examens par Coloration de Graphes
# L2 Informatique — Théorie des Graphes 2025-2026
# ============================================================

import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from donnees import UES, get_etudiants_par_ue, SURVEILLANTS, INTERDICTIONS


class GrapheConflits:
    """
    Représente le graphe de conflits entre UE.
    - Chaque sommet = une UE
    - Chaque arête = conflit (étudiants communs OU même surveillant)
    """

    def __init__(self):
        self.ues = {ue["code"]: ue for ue in UES}
        self.codes = [ue["code"] for ue in UES]
        self.n = len(self.codes)
        self.index = {code: i for i, code in enumerate(self.codes)}

        # Matrice d'adjacence (n x n)
        self.matrice_adj = [[0] * self.n for _ in range(self.n)]

        # Liste d'adjacence : dict code -> set de codes voisins
        self.liste_adj = {code: set() for code in self.codes}

        # Raisons des conflits (pour affichage)
        self.raisons = {}

        self._construire_graphe()

    # ----------------------------------------------------------
    # Construction du graphe
    # ----------------------------------------------------------

    def _construire_graphe(self):
        """Construit les arêtes selon toutes les sources de conflits."""
        etudiants_par_ue = get_etudiants_par_ue()

        # 1) Conflits par étudiants communs
        for i, code_a in enumerate(self.codes):
            for j, code_b in enumerate(self.codes):
                if i >= j:
                    continue
                communs = etudiants_par_ue.get(code_a, set()) & \
                          etudiants_par_ue.get(code_b, set())
                if communs:
                    self._ajouter_arete(code_a, code_b, f"{len(communs)} étudiant(s) commun(s)")

        # 2) Conflits par même surveillant
        for i, code_a in enumerate(self.codes):
            for j, code_b in enumerate(self.codes):
                if i >= j:
                    continue
                surv_a = SURVEILLANTS.get(code_a)
                surv_b = SURVEILLANTS.get(code_b)
                if surv_a and surv_b and surv_a == surv_b:
                    self._ajouter_arete(code_a, code_b, f"même surveillant ({surv_a})")

        # 3) Interdictions explicites
        for code_a, code_b in INTERDICTIONS:
            if code_a in self.liste_adj and code_b in self.liste_adj:
                self._ajouter_arete(code_a, code_b, "interdiction explicite")

    def _ajouter_arete(self, code_a, code_b, raison=""):
        """Ajoute une arête entre deux sommets (évite les doublons)."""
        i, j = self.index[code_a], self.index[code_b]
        if not self.matrice_adj[i][j]:
            self.matrice_adj[i][j] = 1
            self.matrice_adj[j][i] = 1
            self.liste_adj[code_a].add(code_b)
            self.liste_adj[code_b].add(code_a)
            cle = tuple(sorted([code_a, code_b]))
            self.raisons[cle] = raison

    # ----------------------------------------------------------
    # Propriétés du graphe
    # ----------------------------------------------------------

    def nb_sommets(self):
        return self.n

    def nb_aretes(self):
        return sum(len(v) for v in self.liste_adj.values()) // 2

    def degre(self, code):
        return len(self.liste_adj[code])

    def voisins(self, code):
        return self.liste_adj[code]

    def afficher_statistiques(self):
        print("\n" + "="*60)
        print("  STATISTIQUES DU GRAPHE DE CONFLITS")
        print("="*60)
        print(f"  Nombre de sommets (UE) : {self.nb_sommets()}")
        print(f"  Nombre d'arêtes (conflits) : {self.nb_aretes()}")
        print()
        print(f"  {'UE':<10} {'Nom':<28} {'Degré':>6}")
        print("  " + "-"*46)
        for code in sorted(self.codes, key=lambda c: self.degre(c), reverse=True):
            nom = self.ues[code]["nom"]
            deg = self.degre(code)
            print(f"  {code:<10} {nom:<28} {deg:>6}")
        print()
        print("  Arêtes et raisons :")
        for (a, b), raison in sorted(self.raisons.items()):
            print(f"    {a} — {b}  ({raison})")
        print("="*60)

    # ----------------------------------------------------------
    # Visualisation avec NetworkX / Matplotlib
    # ----------------------------------------------------------

    def visualiser(self, couleurs=None, chemin_sortie="graphe_conflits.png"):
        """
        Affiche le graphe. Si couleurs est fourni (dict code->int),
        colorie les sommets selon les créneaux assignés.
        """
        G = nx.Graph()

        # Ajout des nœuds
        for code in self.codes:
            G.add_node(code, label=f"{code}\n{self.ues[code]['nom'][:12]}")

        # Ajout des arêtes
        for code_a in self.codes:
            for code_b in self.liste_adj[code_a]:
                if code_a < code_b:
                    G.add_edge(code_a, code_b)

        # Palette de couleurs pour les créneaux
        palette = [
            "#E74C3C", "#3498DB", "#2ECC71", "#F39C12",
            "#9B59B6", "#1ABC9C", "#E67E22", "#34495E",
            "#E91E63", "#00BCD4", "#8BC34A", "#FF5722",
        ]

        if couleurs:
            nb_couleurs = max(couleurs.values()) + 1
            node_colors = [palette[couleurs.get(n, 0) % len(palette)] for n in G.nodes()]
        else:
            node_colors = ["#95A5A6"] * len(G.nodes())
            nb_couleurs = 0

        # Disposition
        pos = nx.spring_layout(G, seed=42, k=2.5)

        fig, ax = plt.subplots(figsize=(14, 10))
        ax.set_facecolor("#1a1a2e")
        fig.patch.set_facecolor("#1a1a2e")

        # Dessin des arêtes
        nx.draw_networkx_edges(
            G, pos, ax=ax,
            edge_color="#7f8c8d",
            width=1.5, alpha=0.6
        )

        # Dessin des nœuds
        nx.draw_networkx_nodes(
            G, pos, ax=ax,
            node_color=node_colors,
            node_size=1200, alpha=0.95
        )

        # Étiquettes des nœuds
        labels = {code: code for code in G.nodes()}
        nx.draw_networkx_labels(
            G, pos, labels=labels, ax=ax,
            font_size=8, font_color="white", font_weight="bold"
        )

        # Titre et légende
        titre = "Graphe de Conflits — Planification d'Examens"
        if couleurs:
            titre += f"\nColoration : {nb_couleurs} créneaux"
        ax.set_title(titre, fontsize=14, fontweight="bold",
                     color="white", pad=15)

        if couleurs:
            legendes = []
            for c in range(nb_couleurs):
                patch = mpatches.Patch(
                    color=palette[c % len(palette)],
                    label=f"Créneau {c+1}"
                )
                legendes.append(patch)
            ax.legend(handles=legendes, loc="upper left",
                      facecolor="#2c2c54", labelcolor="white",
                      fontsize=8, framealpha=0.8)

        ax.axis("off")
        plt.tight_layout()
        plt.savefig(chemin_sortie, dpi=150, bbox_inches="tight",
                    facecolor=fig.get_facecolor())
        plt.close()
        print(f"\n  ✅ Graphe sauvegardé : {chemin_sortie}")
        return chemin_sortie
