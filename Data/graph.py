import numpy as np
from typing import Dict, List, Set

from .models import UE


class ConflictGraph:
    """
    Représente le graphe de conflits entre les UEs.
    Contient à la fois une matrice d'adjacence et une liste d'adjacence.
    """

    def __init__(self, ues: List[UE]):
        self.ues = ues
        self.ue_map = {ue.id: i for i, ue in enumerate(ues)}
        self.num_vertices = len(ues)
        self.adj_matrix = np.zeros((self.num_vertices, self.num_vertices), dtype=int)
        self.adj_list: Dict[str, Set[str]] = {ue.id: set() for ue in ues}
        self._build_graph()

    def _add_edge(self, ue1: UE, ue2: UE):
        if ue1.id == ue2.id:
            return
        i, j = self.ue_map[ue1.id], self.ue_map[ue2.id]
        if self.adj_matrix[i][j] == 0:
            self.adj_matrix[i][j] = 1
            self.adj_matrix[j][i] = 1
            self.adj_list[ue1.id].add(ue2.id)
            self.adj_list[ue2.id].add(ue1.id)

    def _build_graph(self):
        """Construit le graphe : conflits étudiants + surveillants communs."""
        for i in range(self.num_vertices):
            for j in range(i + 1, self.num_vertices):
                ue1 = self.ues[i]
                ue2 = self.ues[j]

                shared_students = ue1.students.intersection(ue2.students)
                shared_surveillant = (
                    ue1.surveillant
                    and ue1.surveillant == ue2.surveillant
                )

                if shared_students or shared_surveillant:
                    self._add_edge(ue1, ue2)

    @property
    def num_edges(self) -> int:
        return int(np.sum(self.adj_matrix) // 2)

    def get_degree(self, ue_id: str) -> int:
        return len(self.adj_list[ue_id])

    def get_all_degrees(self) -> Dict[str, int]:
        return {ue_id: len(neighbors) for ue_id, neighbors in self.adj_list.items()}

    def display_stats(self):
        print("--- Statistiques du Graphe ---")
        print(f"Nombre de sommets (UEs) : {self.num_vertices}")
        print(f"Nombre d'arêtes (conflits) : {self.num_edges}")
        print("Degrés des sommets :")
        for ue_id, degree in sorted(self.get_all_degrees().items()):
            print(f"  - {ue_id} : {degree}")
        print("-" * 30)
