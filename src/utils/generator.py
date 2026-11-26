from typing import List
from src.models.score import Note, Score


def build_complex_ensemble_piece() -> Score:
    """
    Construye una pieza polifónica compleja de 8 compases en DO Mayor / LA menor
    con melodía ornamentada, acordes abiertos de 4 notas y duplicaciones octavadas.
    """
    notes: List[Note] = []
    # Progresión de 4 acordes por ciclo (2 ciclos = 8 compases de 2 segundos cada uno)
    progression = [
        # (tiempo_inicio, bajo_midi, notas_acorde, melodia_rapida)
        (0.0, 36, [48, 55, 60, 64, 67, 72], [76, 79, 81, 79, 76, 74, 72, 74]),  # C Major denso
        (2.0, 33, [45, 52, 57, 60, 64, 69], [72, 76, 79, 81, 84, 81, 79, 76]),  # Am7 denso
        (4.0, 29, [41, 48, 53, 57, 60, 65], [69, 72, 76, 77, 81, 77, 76, 72]),  # FMaj7 denso
        (6.0, 31, [43, 50, 55, 59, 62, 67], [71, 74, 77, 79, 83, 79, 77, 74]),  # G7 denso
    ]

    for bar_t, bass_p, chord_pitches, mel_pitches in progression:
        # Bajo octavado (difícil por salto de octava simultáneo)
        notes.append(Note(pitch=bass_p, onset=bar_t, duration=1.8, role="bass", multiplicity=2))
        notes.append(Note(pitch=bass_p + 12, onset=bar_t, duration=1.8, role="bass", multiplicity=1))

        # Acordes en bloque cada 0.5s (alta densidad armónica)
        for beat in range(4):
            t_beat = bar_t + beat * 0.5
            for cp in chord_pitches:
                notes.append(Note(pitch=cp, onset=t_beat, duration=0.45, role="harmony", multiplicity=1))

        # Melodía principal en semicorcheas (cada 0.25s)
        for i, mp in enumerate(mel_pitches):
            t_mel = bar_t + i * 0.25
            notes.append(Note(pitch=mp, onset=t_mel, duration=0.23, role="melody", multiplicity=3))

    return Score(notes, title="Ensamble_Original_Dificil")