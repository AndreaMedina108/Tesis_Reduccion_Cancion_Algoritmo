import csv
import os
import struct
from src.models.score import Score


def export_score_to_csv(score: Score, filepath: str) -> None:
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["onset_s", "duration_s", "pitch_midi", "hand", "role", "multiplicity"])
        for n in score.notes:
            writer.writerow([
                round(n.onset, 3),
                round(n.duration, 3),
                n.pitch,
                n.hand,
                n.role,
                n.multiplicity,
            ])


def _vlq(value: int) -> bytes:
    """Codifica un entero en formato Variable-Length Quantity estándar de MIDI."""
    chunks = [value & 0x7F]
    value >>= 7
    while value:
        chunks.append((value & 0x7F) | 0x80)
        value >>= 7
    return bytes(reversed(chunks))


def export_score_to_midi(score: Score, filepath: str, bpm: int = 120) -> None:
    """Genera un archivo MIDI (.mid) Formato 1 con dos pistas: Mano Derecha (0) y Mano Izquierda (1)."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    ticks_per_beat = 480
    sec_per_beat = 60.0 / bpm

    def build_track_bytes(notes_list, channel: int) -> bytes:
        events = []
        for n in notes_list:
            start_tick = int(round((n.onset / sec_per_beat) * ticks_per_beat))
            end_tick = int(round(((n.onset + n.duration) / sec_per_beat) * ticks_per_beat))
            vel = 95 if n.role == "melody" else (85 if n.role == "bass" else 68)
            events.append((start_tick, 0x90 | channel, n.pitch, vel))
            events.append((max(start_tick + 1, end_tick), 0x80 | channel, n.pitch, 0))

        events.sort(key=lambda e: (e[0], 0 if (e[1] & 0xF0) == 0x80 else 1))
        track_data = bytearray()
        last_tick = 0
        for tick, status, pitch, vel in events:
            delta = max(0, tick - last_tick)
            track_data.extend(_vlq(delta))
            track_data.extend(bytes([status, pitch, vel]))
            last_tick = tick

        track_data.extend(b"\x00\xFF\x2F\x00")  # Fin de pista
        return b"MTrk" + struct.pack(">I", len(track_data)) + bytes(track_data)

    r_notes = score.get_hand_notes("R")
    l_notes = score.get_hand_notes("L")

    header = b"MThd" + struct.pack(">IHHH", 6, 1, 2, ticks_per_beat)
    track_r = build_track_bytes(r_notes, channel=0)
    track_l = build_track_bytes(l_notes, channel=1)

    with open(filepath, "wb") as f:
        f.write(header + track_r + track_l)