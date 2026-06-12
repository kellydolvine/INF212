import numpy as np
if not hasattr(np, 'int'):
    np.int = int

import networkx as nx
import matplotlib
matplotlib.use('Agg')  # Backend non-interactif pour éviter les erreurs d'affichage
import matplotlib.pyplot as plt
import math
import os
from collections import defaultdict
from typing import Any, Dict, List, Optional

from Data.graph import ConflictGraph
from Data.models import Creneau

FILIERE_COLORS = {
    "INF": "#4E79A7",
    "MATH": "#F28E2B",
    "CHIM": "#59A14F",
    "PHY": "#E15759",
}


class GraphPlotter:
    """Outils de visualisation pour le graphe de conflits et le planning."""

    COLOR_PALETTE = [
        '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4',
        '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F',
        '#BB8FCE', '#85C1E9', '#F0B27A', '#82E0AA',
        '#F1948A', '#AED6F1', '#D5F5E3', '#FADBD8',
    ]

    @staticmethod
    def plot_colored_graph(
        graph: ConflictGraph,
        coloring: Dict[str, int],
        filename: str,
        creneaux: Optional[List[Creneau]] = None,
    ):
        """
        Affiche et sauvegarde le graphe coloré.
        Utilise matplotlib directement pour éviter les problèmes de compatibilité
        entre networkx 2.4 et matplotlib 3.7+.
        """
        G = nx.Graph()

        # Ajouter les sommets
        G.add_nodes_from([ue.id for ue in graph.ues])

        # Ajouter les arêtes (une seule fois par paire)
        added_edges = set()
        for ue_id, neighbors in graph.adj_list.items():
            for neighbor in neighbors:
                edge = tuple(sorted([ue_id, neighbor]))
                if edge not in added_edges:
                    G.add_edge(ue_id, neighbor)
                    added_edges.add(edge)

        pos = GraphPlotter._filiere_layout(graph.ues)
        num_colors = max(coloring.values()) + 1 if coloring else 1
        palette = GraphPlotter.COLOR_PALETTE
        node_colors = [palette[coloring.get(n, 0) % len(palette)] for n in G.nodes()]

        fig, ax = plt.subplots(figsize=(16, 12))
        nx.draw_networkx_edges(
            G, pos, ax=ax, edge_color="#555555", width=1.5, alpha=0.55
        )
        nx.draw_networkx_nodes(
            G, pos, ax=ax, node_color=node_colors,
            node_size=2200, edgecolors="#222222", linewidths=2.5
        )
        nx.draw_networkx_labels(
            G, pos, ax=ax, font_size=9, font_weight="bold", font_color="white"
        )

        # Légende des créneaux
        legend_handles = []
        for i in range(num_colors):
            patch = plt.Rectangle((0, 0), 1, 1, fc=palette[i % len(palette)])
            legend_handles.append(patch)
        def slot_label(i: int) -> str:
            if creneaux and i < len(creneaux):
                c = creneaux[i]
                return f"{c.id}\n{c.jour} {c.plage}"
            return f"Créneau {i + 1}"

        ax.legend(
            legend_handles,
            [slot_label(i) for i in range(num_colors)],
            loc="upper left", fontsize=9, title="Créneaux horaires", framealpha=0.9,
        )
        ax.set_title(
            f"Graphe de conflits coloré — {num_colors} créneaux nécessaires\n"
            f"(arête = conflit étudiant ou surveillant)",
            fontsize=15, fontweight="bold", pad=16,
        )
        ax.axis("off")
        GraphPlotter._save_fig(fig, filename)

    @staticmethod
    def _filiere_layout(ues):
        centers = {"INF": (2, 2), "MATH": (-2, 2), "CHIM": (-2, -2), "PHY": (2, -2)}
        by_filiere = defaultdict(list)
        for ue in ues:
            by_filiere[ue.filiere].append(ue.id)
        pos = {}
        for filiere, nodes in by_filiere.items():
            cx, cy = centers.get(filiere, (0, 0))
            nodes = sorted(nodes)
            for i, node in enumerate(nodes):
                angle = 2 * math.pi * i / max(len(nodes), 1)
                pos[node] = (cx + 0.9 * math.cos(angle), cy + 0.9 * math.sin(angle))
        return pos

    @staticmethod
    def _save_fig(fig, filename):
        os.makedirs(os.path.dirname(filename) or ".", exist_ok=True)
        fig.savefig(filename, dpi=200, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        print(f"Image sauvegardée : {filename}")

    @staticmethod
    def _build_graph(graph: ConflictGraph) -> nx.Graph:
        G = nx.Graph()
        G.add_nodes_from([ue.id for ue in graph.ues])
        seen = set()
        for ue_id, neighbors in graph.adj_list.items():
            for neighbor in neighbors:
                edge = tuple(sorted([ue_id, neighbor]))
                if edge not in seen:
                    G.add_edge(*edge)
                    seen.add(edge)
        return G

    @staticmethod
    def plot_conflict_graph(graph: ConflictGraph, filename: str):
        G = GraphPlotter._build_graph(graph)
        pos = GraphPlotter._filiere_layout(graph.ues)
        ue_filiere = {ue.id: ue.filiere for ue in graph.ues}
        node_colors = [FILIERE_COLORS.get(ue_filiere[n], "#999999") for n in G.nodes()]

        fig, ax = plt.subplots(figsize=(16, 12))
        nx.draw_networkx_edges(G, pos, ax=ax, edge_color="#444444", width=2, alpha=0.7)
        nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors, node_size=2400,
                               edgecolors="#111111", linewidths=2.5)
        nx.draw_networkx_labels(G, pos, ax=ax, font_size=9, font_weight="bold", font_color="white")

        handles = [plt.Rectangle((0, 0), 1, 1, fc=c) for c in FILIERE_COLORS.values()]
        ax.legend(handles, list(FILIERE_COLORS.keys()), title="Filières", loc="upper left")
        ax.set_title(
            f"Graphe de conflits ({graph.num_vertices} UEs, {graph.num_edges} arêtes)\n"
            "Une arête relie deux UEs incompatibles au même créneau",
            fontsize=15, fontweight="bold", pad=16,
        )
        ax.axis("off")
        GraphPlotter._save_fig(fig, filename)
