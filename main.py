import numpy as np
if not hasattr(np, "int"):
    np.int = int

from Data.loader import load_data
from Data.graph import ConflictGraph
from Algo.coloration import ColoringAlgorithms
from Algo.assignment import Scheduler
from Visualization.plotter import GraphPlotter


def main():
    print("=== SYSTÈME DE PLANIFICATION D'EXAMENS (COLORATION DE GRAPHES) ===\n")

    ues, rooms, students, creneaux = load_data()
    print(
        f"Données chargées : {len(ues)} UEs, {len(rooms)} salles, "
        f"{len(students)} étudiants, {len(creneaux)} créneaux "
        f"({len(creneaux) // 4} jours × 4 plages, 2 semaines)."
    )

    print("\nPhase 1 : Construction du graphe de conflits...")
    graph = ConflictGraph(ues)
    graph.display_stats()

    print("\nPhase 2 : Coloration du graphe...")
    print("\n[Algo 1] Welsh-Powell :")
    wp_colors = ColoringAlgorithms.welsh_powell(graph)

    print("\n[Algo 2] DSATUR :")
    dsat_colors = ColoringAlgorithms.dsatur(graph)

    wp_slots = max(wp_colors.values()) + 1 if wp_colors else 0
    dsat_slots = max(dsat_colors.values()) + 1 if dsat_colors else 0
    print(
        f"\nComparaison : Welsh-Powell → {wp_slots} créneaux | "
        f"DSATUR → {dsat_slots} créneaux"
    )

    chosen_colors = dsat_colors if dsat_slots <= wp_slots else wp_colors
    algo_name = "DSATUR" if dsat_slots <= wp_slots else "Welsh-Powell"
    print(f"Algorithme retenu pour le planning : {algo_name}")

    if max(chosen_colors.values()) + 1 > len(creneaux):
        print(
            f"\n[ATTENTION] {max(chosen_colors.values()) + 1} créneaux nécessaires "
            f"pour {len(creneaux)} disponibles."
        )

    print("\nPhase 3 : Affectation des salles et audit...")
    scheduler = Scheduler(rooms, creneaux)
    schedule = scheduler.assign_rooms(chosen_colors, ues)
    scheduler.audit_constraints(schedule, ues, graph.adj_list)

    export_path = "Export/planning_final.csv"
    scheduler.export_csv(schedule, export_path)

    print("\nPhase 4 : Visualisation du graphe...")
    viz_path = "Visualization/graphe_colore.png"
    GraphPlotter.plot_colored_graph(graph, chosen_colors, viz_path, creneaux)

    print("\n" + "=" * 50)
    print("PROJET TERMINÉ — DONNÉES RÉELLES (2 SEMAINES)")
    print(f"Planning : {export_path}")
    print(f"Graphe   : {viz_path}")
    print("=" * 50)


if __name__ == "__main__":
    main()
