import networkx as nx
import matplotlib.pyplot as plt
import csv
import numpy as np
from collections import defaultdict

# =========================
# 1. DATA
# =========================

ues = [
    "INF212",
    "INF222",
    "INF232",
    "MATH232",
    "PPE212",
    "INF242",
    "INF252"
]

obligatoires = [
    "INF212",
    "INF222",
    "INF232",
    "MATH232",
    "PPE212"
]

effectifs = {
    "INF212": 100,
    "INF222": 100,
    "INF232": 100,
    "MATH232": 100,
    "PPE212": 100,
    "INF242": 50,
    "INF252": 50
}

salles = [
    {"nom": "Amphi1001", "capacite": 1000},
    {"nom": "Amphi1002", "capacite": 1000},
    {"nom": "Amphi350", "capacite": 350},
    {"nom": "Amphi502", "capacite": 502}
]

creneaux = [
    "Lundi 07h30-10h30",
    "Lundi 11h00-14h00",
    "Mardi 07h30-10h30",
    "Mardi 11h00-14h00",
    "Mercredi 07h30-10h30",
    "Mercredi 11h00-14h00"
]

# =========================
# 2. GRAPH CONSTRUCTION (CORRECTED CONFLICTS)
# =========================

G = nx.Graph()
G.add_nodes_from(ues)

# All obligatory UE conflict with each other
for i in range(len(obligatoires)):
    for j in range(i + 1, len(obligatoires)):
        G.add_edge(obligatoires[i], obligatoires[j])

# INF242 and INF252 conflict with ALL obligatory UEs
for oblig in obligatoires:
    G.add_edge("INF242", oblig)
    G.add_edge("INF252", oblig)

# INF242 and INF252 can be together (no edge between them)

print("Nombre de sommets :", G.number_of_nodes())
print("Nombre d'arêtes :", G.number_of_edges())

for sommet in G.nodes():
    print(f"Degré({sommet}) = {G.degree(sommet)}")

# =========================
# 3. WELSH-POWELL
# =========================

def welsh_powell(graph):
    sommets = sorted(graph.nodes(), key=lambda x: graph.degree(x), reverse=True)
    couleurs = {}
    couleur = 0

    for sommet in sommets:
        if sommet not in couleurs:
            couleur += 1
            couleurs[sommet] = couleur

            for autre in sommets:
                if autre not in couleurs:
                    conflit = False
                    for s in couleurs:
                        if couleurs[s] == couleur and graph.has_edge(s, autre):
                            conflit = True
                            break

                    if not conflit:
                        couleurs[autre] = couleur

    return couleurs

resultat = welsh_powell(G)

# =========================
# 4. DISPLAY COLORING
# =========================

print("\n===== COLORATION =====")
print("-" * 40)
for ue, creneau in sorted(resultat.items(), key=lambda x: x[1]):
    print(f"{ue:10} -> Couleur {creneau}")
print("-" * 40)

# =========================
# 5. MAP COLORS TO TIME SLOTS
# =========================

color_to_creneau = {}
for i, c in enumerate(sorted(set(resultat.values()))):
    if i < len(creneaux):
        color_to_creneau[c] = creneaux[i]
    else:
        color_to_creneau[c] = f"Créneau supplémentaire {i+1}"

# =========================
# 6. ROOM ALLOCATION (one exam per room per slot)
# =========================

# Group UEs by time slot (color)
ue_by_time_slot = defaultdict(list)
for ue, color in resultat.items():
    time_slot = color_to_creneau[color]
    ue_by_time_slot[time_slot].append((ue, effectifs[ue]))

planning_final = []
used_rooms_per_slot = defaultdict(set)  # Track which rooms are used in each time slot

# Sort rooms by capacity (smallest first for better fit)
salles_sorted = sorted(salles, key=lambda x: x["capacite"])

for time_slot, ue_list in ue_by_time_slot.items():
    # Sort UEs by size (largest first) for optimal room assignment
    ue_list_sorted = sorted(ue_list, key=lambda x: x[1], reverse=True)
    
    for ue, nb_etudiants in ue_list_sorted:
        # Find an available room that fits and is not used in this time slot
        salle_attribuee = None
        
        for salle in salles_sorted:
            if (salle["capacite"] >= nb_etudiants and 
                salle["nom"] not in used_rooms_per_slot[time_slot]):
                salle_attribuee = salle["nom"]
                used_rooms_per_slot[time_slot].add(salle["nom"])
                break
        
        if salle_attribuee is None:
            salle_attribuee = "❌ AUCUNE SALLE DISPONIBLE"
        
        planning_final.append((ue, time_slot, salle_attribuee, nb_etudiants))

# =========================
# 7. FINAL TIMETABLE DISPLAY
# =========================

print("\n" + "="*90)
print(" " * 30 + "📋 PLANNING FINAL DES EXAMENS 📋")
print("="*90)
print()

# Group by day/time slot
planning_by_slot = defaultdict(list)
for ue, creneau, salle, nb in planning_final:
    planning_by_slot[creneau].append((ue, salle, nb))

# Display organized by time slot
for creneau in sorted(planning_by_slot.keys()):
    print(f"🕐 {creneau}")
    print("-" * 90)
    print(f"{'UE':<15} {'Effectif':<12} {'Salle':<25}")
    print("-" * 90)
    
    for ue, salle, nb in sorted(planning_by_slot[creneau]):
        print(f"{ue:<15} {nb:<12} {salle:<25}")
    print()
    print(f"📌 {len(planning_by_slot[creneau])} examen(s) dans ce créneau")
    print()

print("="*90)
print(f"📊 RÉSUMÉ: {len(planning_final)} UE planifiées sur {len(creneaux)} créneaux disponibles")
print("="*90)

# =========================
# 8. VERIFICATION OF CONFLICTS
# =========================

print("\n" + "="*90)
print("🔍 VÉRIFICATION DES CONTRAINTES")
print("="*90)

has_conflict = False

# Check pedagogical conflicts (graph edges)
for time_slot, ue_list in planning_by_slot.items():
    ue_names = [ue for ue, _, _ in ue_list]
    for i in range(len(ue_names)):
        for j in range(i+1, len(ue_names)):
            if G.has_edge(ue_names[i], ue_names[j]):
                print(f"❌ CONFLIT PÉDAGOGIQUE: {ue_names[i]} et {ue_names[j]} sont en conflit et programmés en même temps ({time_slot})")
                has_conflict = True

# Check room conflicts (same room used twice in same slot)
for time_slot, ue_list in planning_by_slot.items():
    rooms_used = {}
    for ue, salle, nb in ue_list:
        if salle in rooms_used:
            print(f"❌ CONFLIT DE SALLE: {ue} et {rooms_used[salle]} partagent la même salle {salle} à {time_slot}")
            has_conflict = True
        else:
            rooms_used[salle] = ue

if not has_conflict:
    print("✅ AUCUN CONFLIT DÉTECTÉ! Le planning respecte toutes les contraintes.")
    
    # Additional info about simultaneous exams
    print("\n📊 Examens simultanés par créneau:")
    for creneau, exams in planning_by_slot.items():
        if len(exams) > 1:
            print(f"   {creneau}: {len(exams)} examens en parallèle (différentes salles)")
        else:
            print(f"   {creneau}: 1 examen")

print("="*90)

# =========================
# 9. CSV EXPORT
# =========================

with open("planning_final.csv", "w", newline="", encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(["UE", "Créneau", "Salle", "Effectif"])
    
    for ue, creneau, salle, nb in planning_final:
        writer.writerow([ue, creneau, salle, nb])

print("\n✅ planning_final.csv généré avec succès!")

# =========================
# 10. VISUALIZATION
# =========================

plt.figure(figsize=(14, 10))

# Create layout
pos = nx.spring_layout(G, k=2, iterations=50, seed=42)

# Get colors for nodes
couleurs_nodes = [resultat[n] for n in G.nodes()]

# Define a nice colormap
colors = plt.cm.Set3(np.linspace(0, 1, max(couleurs_nodes)))

# Draw edges
nx.draw_networkx_edges(G, pos, 
                       edge_color='gray', 
                       width=2.5, 
                       alpha=0.7,
                       style='solid')

# Draw nodes
for node in G.nodes():
    color_idx = resultat[node] - 1
    nx.draw_networkx_nodes(G, pos, 
                          nodelist=[node],
                          node_color=[colors[color_idx]],
                          node_size=3500,
                          edgecolors='black',
                          linewidths=2.5,
                          alpha=0.9)

# Add labels
labels = {node: node for node in G.nodes()}
nx.draw_networkx_labels(G, pos, labels, 
                       font_size=11, 
                       font_weight='bold')

# Add degree information
degree_labels = {node: f"deg={G.degree(node)}" for node in G.nodes()}
for node, (x, y) in pos.items():
    plt.text(x, y-0.12, degree_labels[node], 
             fontsize=9, ha='center', va='top',
             bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))

# Add legend
legend_elements = []
unique_colors = sorted(set(resultat.values()))
for color_num in unique_colors:
    creneau_associe = color_to_creneau[color_num]
    legend_elements.append(plt.Rectangle((0,0),1,1, 
                                        facecolor=colors[color_num-1], 
                                        edgecolor='black',
                                        label=f'Couleur {color_num}: {creneau_associe[:20]}...'))

plt.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1, 1), fontsize=10)

plt.title("Coloration du graphe des examens - Algorithme Welsh-Powell\n" + 
          "Chaque couleur représente un créneau horaire différent\n" +
          "INF242 et INF252 sont en conflit avec TOUTES les UE obligatoires\n" +
          "Les arêtes représentent les conflits (examens impossibles à programmer en même temps)",
          fontsize=14, fontweight='bold', pad=20)

plt.axis('off')
plt.tight_layout()
plt.savefig("graphe_colore.png", dpi=300, bbox_inches='tight')
plt.show()

# =========================
# 11. STATISTICS
# =========================

print("\n" + "="*90)
print("📈 STATISTIQUES D'UTILISATION DES SALLES")
print("="*90)

room_usage = {}
for _, _, salle, nb in planning_final:
    if salle not in room_usage:
        room_usage[salle] = {"count": 0, "total_students": 0}
    if "AUCUNE" not in salle:
        room_usage[salle]["count"] += 1
        room_usage[salle]["total_students"] += nb

for salle, stats in room_usage.items():
    print(f"🏛️  {salle:<15} : {stats['count']} examen(s), {stats['total_students']} étudiants")

# Show which UEs share time slots
print("\n📋 DÉTAIL DES CRÉNEAUX:")
for creneau, exams in sorted(planning_by_slot.items()):
    print(f"\n{creneau}:")
    for ue, salle, nb in exams:
        print(f"   - {ue} ({nb} étudiants) -> {salle}")
