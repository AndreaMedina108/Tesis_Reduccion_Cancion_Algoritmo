import math
from typing import List, Tuple
from src.metrics.difficulty import DifficultyEvaluator
from src.models.importance import compute_musical_importance
from src.models.score import Note, Score


class IterativePianoReducer:
    def __init__(
        self,
        evaluator: DifficultyEvaluator,
        kappa: float = 2.2,
        decay_lambda: float = 0.85,
        max_iter: int = 40,
    ):
        self.evaluator = evaluator
        self.kappa = kappa
        self.decay_lambda = decay_lambda
        self.max_iter = max_iter

    def _assign_hand_and_octave_shift(self, notes: List[Note]) -> List[Note]:
        """
        Asigna cada nota a mano izquierda (L, < C4=60) o derecha (R, >= C4=60)
        y aplica saltos de octava (+12 / -12) si la apertura simultánea excede 12 semitonos (Ec. 10).
        """
        adjusted: List[Note] = []
        for n in notes:
            hand = "L" if n.pitch < 60 else "R"
            pitch = n.pitch
            # Mantener registro cómodo de piano (A1=33 a C7=96) mediante transporte de octava
            while pitch < 36:
                pitch += 12
            while pitch > 96:
                pitch -= 12
            adjusted.append(n.clone(pitch=pitch, hand=hand))

        # Compactar acordes abiertos demasiado anchos en la misma mano mediante octavación
        by_onset = {}
        for idx, n in enumerate(adjusted):
            key = (round(n.onset, 3), n.hand)
            by_onset.setdefault(key, []).append(idx)

        for key, idxs in by_onset.items():
            if len(idxs) <= 1:
                continue
            pitches = [adjusted[i].pitch for i in idxs]
            min_p, max_p = min(pitches), max(pitches)
            if max_p - min_p > 12:
                for i in idxs:
                    # Si es nota interna (no melodía ni bajo extremo), acercarla una octava
                    if adjusted[i].role == "harmony":
                        if adjusted[i].pitch == max_p and max_p - 12 >= min_p:
                            adjusted[i].pitch -= 12
                        elif adjusted[i].pitch == min_p and min_p + 12 <= max_p:
                            adjusted[i].pitch += 12

        return adjusted

    def reduce(
        self,
        ensemble_score: Score,
        target_difficulty: Tuple[float, float, float] = (30.0, 30.0, 40.0),
        label: str = "Reduced",
    ) -> Score:
        """
        Algoritmo iterativo de reducción controlado por restricciones de dificultad (Sección III.B.2).
        target_difficulty = (D_L_tilde, D_R_tilde, D_B_tilde)
        """
        target_l, target_r, target_b = target_difficulty

        # Paso 0: Asignación de manos y compresión por octavas
        working_notes = self._assign_hand_and_octave_shift(ensemble_score.notes)
        # Eliminar duplicados exactos (mismo pitch, mano y tiempo) tras transporte de octava
        unique_map = {}
        for n in working_notes:
            key = (round(n.onset, 3), n.pitch, n.hand)
            if key not in unique_map or compute_musical_importance(n) > compute_musical_importance(unique_map[key]):
                unique_map[key] = n
        working_notes = list(unique_map.values())

        # Inicializar zeta(m) = 1.0 para todas las notas
        zeta = {id(n): 1.0 for n in working_notes}

        for iteration in range(1, self.max_iter + 1):
            current_score = Score(working_notes, title=label)
            eval_details = self.evaluator.compute_note_difficulties(current_score)

            # Paso (ii): Detectar notas que violan las restricciones de dificultad (Ec. 14)
            violating_onsets = [
                note.onset
                for (note, dl, dr, db) in eval_details
                if dl > target_l or dr > target_r or db > target_b
            ]

            if not violating_onsets:
                break

            # Paso (iii): Reducir zeta(m) en las regiones conflictivas (Ec. 17) y podar notas no esenciales
            half_w = self.evaluator.delta_t / 2.0
            candidates_to_remove = []

            for n in working_notes:
                in_conflict_zone = any(abs(n.onset - t_v) <= half_w for t_v in violating_onsets)
                if in_conflict_zone:
                    zeta[id(n)] *= self.decay_lambda
                    h_m = compute_musical_importance(n)
                    # Probabilidad de eliminación beta_NP(m) (Ec. 12)
                    beta_np = (1.0 - zeta[id(n)]) * math.exp(-self.kappa * h_m)
                    candidates_to_remove.append((beta_np, -h_m, n))

            if not candidates_to_remove:
                break

            # Ordenar por mayor probabilidad de eliminación (menor importancia musical)
            candidates_to_remove.sort(key=lambda item: (item[0], item[1]), reverse=True)

            # Eliminar la nota menos esencial en las zonas conflictivas en esta iteración
            removed = False
            for beta_np, _, cand in candidates_to_remove:
                # Nunca eliminar la melodía principal a menos que la densidad sea extrema
                if cand.role != "melody" and beta_np > 0.15:
                    working_notes.remove(cand)
                    removed = True
                    break

            # Si solo quedan notas de melodía/bajo y aún excede el límite, permitir aligerar notas de paso
            if not removed:
                non_melody = [c[2] for c in candidates_to_remove if c[2].role != "melody"]
                if non_melody:
                    working_notes.remove(non_melody[0])
                else:
                    break

        return Score(working_notes, title=label)