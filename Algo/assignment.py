import csv
import os
from typing import Dict, List, Any, Optional

from Data.models import Creneau, UE, Room


class Scheduler:
    """Gère l'affectation des salles et la génération du planning final."""

    def __init__(self, rooms: List[Room], creneaux: Optional[List[Creneau]] = None):
        self.rooms = sorted(rooms, key=lambda r: r.capacity, reverse=True)
        self.creneaux = creneaux or []

    def _creneau_label(self, slot: int) -> str:
        if 0 <= slot < len(self.creneaux):
            c = self.creneaux[slot]
            return f"{c.id} — {c.label}"
        return f"Créneau {slot + 1}"

    def assign_rooms(self, coloring: Dict[str, int], ues: List[UE]) -> List[Dict[str, Any]]:
        """Assigne une salle à chaque UE colorée (chaque couleur = un créneau)."""
        schedule = []
        slots: Dict[int, List[UE]] = {}

        for ue_id, slot in coloring.items():
            slots.setdefault(slot, [])
            ue_obj = next(ue for ue in ues if ue.id == ue_id)
            slots[slot].append(ue_obj)

        for slot, slot_ues in slots.items():
            slot_ues_sorted = sorted(slot_ues, key=lambda u: u.student_count, reverse=True)
            available_rooms = list(self.rooms)

            for ue in slot_ues_sorted:
                assigned_room = None

                for room in available_rooms:
                    if room.capacity < ue.student_count:
                        continue
                    if ue.is_lab and not room.is_lab:
                        continue

                    assigned_room = room
                    available_rooms.remove(room)
                    break

                entry = {
                    "slot": slot,
                    "creneau": self._creneau_label(slot),
                    "ue_id": ue.id,
                    "ue_name": ue.name,
                    "filiere": ue.filiere,
                    "room_id": assigned_room.id if assigned_room else "NON AFFECTÉ",
                    "students": ue.student_count,
                    "is_lab": ue.is_lab,
                    "surveillant": ue.surveillant,
                }
                if not assigned_room:
                    entry["error"] = "Aucune salle disponible"
                schedule.append(entry)

        return schedule

    def export_csv(self, schedule: List[Dict[str, Any]], filename: str):
        """Exporte le planning au format CSV (Créneau × Salle)."""
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        slots = sorted({item["slot"] for item in schedule})
        room_ids = [r.id for r in self.rooms]

        table = {slot: {room: "" for room in room_ids} for slot in slots}
        for item in schedule:
            if item["room_id"] in table[item["slot"]]:
                table[item["slot"]][item["room_id"]] = (
                    f"{item['ue_id']} ({item['students']} pers)"
                )

        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Créneau / Salle"] + room_ids)

            for slot in slots:
                row_label = schedule[next(
                    i for i, s in enumerate(schedule) if s["slot"] == slot
                )]["creneau"]
                row = [row_label]
                for room in room_ids:
                    row.append(table[slot][room])
                writer.writerow(row)

        print(f"Planning exporté avec succès dans : {filename}")

    def audit_constraints(
        self,
        schedule: List[Dict[str, Any]],
        ues: List[UE],
        graph_adj: Optional[Dict[str, set]] = None,
    ):
        """Vérifie le respect des contraintes obligatoires."""
        print("\n--- Rapport d'Audit du Planning ---")
        errors = 0
        warnings = 0

        assigned_ue_ids = {item["ue_id"] for item in schedule}
        for ue in ues:
            if ue.id not in assigned_ue_ids:
                print(f"[ALERTE] L'UE {ue.id} n'est pas programmée.")
                errors += 1

        slot_by_ue = {item["ue_id"]: item["slot"] for item in schedule}

        if graph_adj:
            checked = set()
            for item in schedule:
                for neighbor in graph_adj.get(item["ue_id"], set()):
                    pair = tuple(sorted([item["ue_id"], neighbor]))
                    if pair in checked:
                        continue
                    checked.add(pair)
                    if neighbor in slot_by_ue and slot_by_ue[neighbor] == item["slot"]:
                        print(
                            f"[ERREUR] Conflit étudiant/surveillant : "
                            f"{item['ue_id']} et {neighbor} au même créneau."
                        )
                        errors += 1

        for i in range(len(schedule)):
            for j in range(i + 1, len(schedule)):
                if (
                    schedule[i]["slot"] == schedule[j]["slot"]
                    and schedule[i]["room_id"] == schedule[j]["room_id"]
                    and schedule[i]["room_id"] != "NON AFFECTÉ"
                ):
                    print(
                        f"[ERREUR] Conflit de salle : {schedule[i]['ue_id']} et "
                        f"{schedule[j]['ue_id']} dans {schedule[i]['room_id']} "
                        f"au créneau {schedule[i]['creneau']}."
                    )
                    errors += 1

        room_map = {r.id: r for r in self.rooms}
        for item in schedule:
            if item["room_id"] == "NON AFFECTÉ":
                print(f"[ERREUR] L'UE {item['ue_id']} n'a pas de salle.")
                errors += 1
                continue

            room = room_map[item["room_id"]]
            if item["students"] > room.capacity:
                print(
                    f"[ERREUR] Capacité dépassée pour {item['ue_id']} "
                    f"(besoin: {item['students']}, salle {room.id}: {room.capacity})."
                )
                errors += 1

            if item["is_lab"] and not room.is_lab:
                print(
                    f"[ERREUR] {item['ue_id']} nécessite un labo "
                    f"mais est en salle standard {room.id}."
                )
                errors += 1

        filiere_slots: Dict[str, List[int]] = {}
        for item in schedule:
            filiere_slots.setdefault(item["filiere"], []).append(item["slot"])

        for filiere, slots in filiere_slots.items():
            slots_sorted = sorted(set(slots))
            for a, b in zip(slots_sorted, slots_sorted[1:]):
                if b - a == 1:
                    print(
                        f"[AVERTISSEMENT] Filière {filiere} : examens consécutifs "
                        f"aux créneaux {a + 1} et {b + 1}."
                    )
                    warnings += 1

        if len(self.creneaux) > 0:
            max_slot = max(item["slot"] for item in schedule) if schedule else -1
            if max_slot >= len(self.creneaux):
                print(
                    f"[ERREUR] Plus de créneaux colorés ({max_slot + 1}) "
                    f"que de créneaux disponibles ({len(self.creneaux)})."
                )
                errors += 1
            else:
                used = max_slot + 1
                print(
                    f"Créneaux utilisés : {used} / {len(self.creneaux)} "
                    f"({2} semaines d'examens)."
                )

        if errors == 0:
            msg = "Audit terminé : toutes les contraintes obligatoires sont respectées."
            if warnings:
                msg += f" ({warnings} avertissement(s) sur l'espacement des filières.)"
            print(msg)
        else:
            print(f"Audit terminé : {errors} erreur(s) détectée(s).")
