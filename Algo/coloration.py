import time
from typing import Dict, List, Set, Any
from Data.graph import ConflictGraph

class ColoringAlgorithms:
    """Implémentation des algorithmes de coloration de graphes."""
    
    @staticmethod
    def welsh_powell(graph: ConflictGraph) -> Dict[str, int]:
        """
        Algorithme Welsh-Powell :
        1. Trier les sommets par degré décroissant.
        2. Colorier avec la plus petite couleur disponible.
        """
        start_time = time.time()
        
        # 1. Trier les UEs par degré décroissant
        sorted_ues = sorted(graph.ues, key=lambda ue: graph.get_degree(ue.id), reverse=True)
        
        colors: Dict[str, int] = {}
        
        # 2. Attribution des couleurs
        for ue in sorted_ues:
            # Identifier les couleurs des voisins
            neighbor_colors = {colors[neighbor_id] for neighbor_id in graph.adj_list[ue.id] if neighbor_id in colors}
            
            # Attribuer la plus petite couleur disponible (0, 1, 2...)
            color = 0
            while color in neighbor_colors:
                color += 1
            colors[ue.id] = color
            
        execution_time = time.time() - start_time
        print(f"Welsh-Powell terminé en {execution_time:.6f}s. Couleurs utilisées : {max(colors.values()) + 1 if colors else 0}")
        return colors

    @staticmethod
    def dsatur(graph: ConflictGraph) -> Dict[str, int]:
        """
        Algorithme DSATUR :
        Choisit à chaque étape le sommet avec le plus haut degré de saturation.
        """
        start_time = time.time()
        
        colors: Dict[str, int] = {}
        num_vertices = graph.num_vertices
        
        # Degré de saturation : nombre de couleurs différentes dans le voisinage
        # Degré initial : degré classique
        ue_ids = [ue.id for ue in graph.ues]
        
        while len(colors) < num_vertices:
            # Calculer le degré de saturation (DSAT) pour les sommets non coloriés
            remaining_ues = [ue_id for ue_id in ue_ids if ue_id not in colors]
            
            if not remaining_ues:
                break
                
            # Choisir le sommet selon DSAT
            # En cas d'égalité, choisir celui avec le plus grand degré dans le graphe initial
            def get_dsat_info(ue_id):
                neighbors = graph.adj_list[ue_id]
                distinct_colors = {colors[n] for n in neighbors if n in colors}
                return (len(distinct_colors), graph.get_degree(ue_id))
            
            best_ue = max(remaining_ues, key=get_dsat_info)
            
            # Attribuer la plus petite couleur disponible
            neighbor_colors = {colors[n] for n in graph.adj_list[best_ue] if n in colors}
            color = 0
            while color in neighbor_colors:
                color += 1
            colors[best_ue] = color
            
        execution_time = time.time() - start_time
        print(f"DSATUR terminé en {execution_time:.6f}s. Couleurs utilisées : {max(colors.values()) + 1 if colors else 0}")
        return colors
