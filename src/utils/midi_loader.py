import mido
from typing import List
from src.models.score import Note, Score


def load_midi_to_score(filepath: str, title: str = "Cancion_Externa") -> Score:
    """
    Lee un archivo MIDI (.mid) externo y lo convierte en un objeto Score,
    detectando automáticamente melodía (voz superior), bajo (voz inferior) y armonía.
    """
    mid = mido.MidiFile(filepath)
    raw_notes = []
    active_notes = {}  # (channel, pitch) -> start_time_sec
    current_time = 0.0

    # 1. Extraer tiempos de inicio (onset) y duraciones en segundos reales
    for msg in mid:
        current_time += msg.time
        if msg.type == "note_on" and msg.velocity > 0:
            key = (getattr(msg, "channel", 0), msg.note)
            if key not in active_notes:
                active_notes[key] = current_time
        elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
            key = (getattr(msg, "channel", 0), msg.note)
            if key in active_notes:
                start_t = active_notes.pop(key)
                dur = max(0.05, current_time - start_t)
                raw_notes.append({"pitch": msg.note, "onset": round(start_t, 3), "duration": round(dur, 3)})

    if not raw_notes:
        raise ValueError(f"No se encontraron notas válidas en el archivo MIDI: {filepath}")

    # 2. Agrupar por ventanas cortas de ataque (40 ms) para identificar roles (melodía, bajo, armonía)
    raw_notes.sort(key=lambda x: (x["onset"], x["pitch"]))
    clusters = []
    current_cluster = [raw_notes[0]]

    for rn in raw_notes[1:]:
        if abs(rn["onset"] - current_cluster[0]["onset"]) <= 0.04:
            current_cluster.append(rn)
        else:
            clusters.append(current_cluster)
            current_cluster = [rn]
    clusters.append(current_cluster)

    final_notes: List[Note] = []
    for cluster in clusters:
        pitches = [c["pitch"] for c in cluster]
        max_p = max(pitches)
        min_p = min(pitches)

        for c in cluster:
            p = c["pitch"]
            mult = pitches.count(p) - 1  # Multiplicidad si varios canales tocan la misma nota

            # Asignación automática de rol musical
            if len(cluster) == 1:
                role = "melody" if p >= 60 else "bass"
            else:
                if p == max_p and p >= 55:
                    role = "melody"
                elif p == min_p and p < 60:
                    role = "bass"
                else:
                    role = "harmony"

            hand = "L" if p < 60 else "R"
            final_notes.append(
                Note(
                    pitch=p,
                    onset=c["onset"],
                    duration=c["duration"],
                    role=role,
                    hand=hand,
                    multiplicity=mult,
                )
            )

    return Score(final_notes, title=title)