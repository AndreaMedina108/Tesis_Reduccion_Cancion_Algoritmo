import math
from typing import Dict, List, Tuple
from src.models.score import HandType, Note, Score


class DifficultyEvaluator:
    def __init__(self, sigma_p: float = 5.5, epsilon: float = 4e-4, delta_t: float = 1.0):
        self.sigma_p = sigma_p
        self.epsilon = epsilon
        self.delta_t = delta_t
        self.ref_pitch = {"L": 48, "R": 72}  # C3 para izquierda, C5 para derecha

    def _gaussian_transition_prob(self, p_curr: int, p_prev: int) -> float:
        """Ecuación (3): P(p_n | p_{n-1}) proporcional a Gauss(p_n; p_{n-1}, sigma_p^2) + eps."""
        diff = p_curr - p_prev
        gauss = math.exp(-0.5 * (diff / self.sigma_p) ** 2) / (self.sigma_p * math.sqrt(2 * math.pi))
        return gauss + self.epsilon

    def _hand_span_penalty(self, simultaneous_notes: List[Note]) -> float:
        """Penaliza acordes cuya extensión supere la apertura cómoda de una mano (> 12 semitonos)."""
        if len(simultaneous_notes) <= 1:
            return 0.0
        pitches = [n.pitch for n in simultaneous_notes]
        span = max(pitches) - min(pitches)
        if span > 12:
            return 2.5 * (span - 12)
        return 0.0

    def compute_note_difficulties(self, score: Score) -> List[Tuple[Note, float, float, float]]:
        """
        Retorna una lista de tuplas (nota, D_L, D_R, D_B) evaluadas en ventanas de ancho delta_t.
        Ecuación (6): D(t) = -ln P(p(t)) / delta_t.
        """
        results = []
        for idx, target in enumerate(score.notes):
            t_min = target.onset - self.delta_t / 2.0
            t_max = target.onset + self.delta_t / 2.0

            d_hand = {"L": 0.0, "R": 0.0}
            for hand in ("L", "R"):
                win_notes = [
                    n for n in score.notes
                    if n.hand == hand and t_min <= n.onset <= t_max
                ]
                if not win_notes:
                    d_hand[hand] = 0.0
                    continue

                # Costo probabilístico acumulado en la ventana
                neg_log_prob = 0.0
                prev_pitch = self.ref_pitch[hand]
                for wn in win_notes:
                    prob = self._gaussian_transition_prob(wn.pitch, prev_pitch)
                    neg_log_prob += -math.log(prob)
                    prev_pitch = wn.pitch

                # Penalización por apertura simultánea excesiva en el instante del ataque
                simul = [wn for wn in win_notes if abs(wn.onset - target.onset) < 1e-3]
                span_cost = self._hand_span_penalty(simul)

                d_hand[hand] = (neg_log_prob + span_cost) / self.delta_t

            d_l = d_hand["L"]
            d_r = d_hand["R"]
            d_b = d_l + d_r
            results.append((target, d_l, d_r, d_b))

        return results

    def summarize_metrics(
        self, score: Score, targets: Tuple[float, float, float]
    ) -> Dict[str, float]:
        """Calcula métricas globales de evaluación (Ecs. 19-22): Media, Máximo y Tasa fuera de rango."""
        target_l, target_r, target_b = targets
        details = self.compute_note_difficulties(score)
        if not details:
            return {"mean_DB": 0.0, "max_DB": 0.0, "out_of_range_pct": 0.0, "add_note_pct": 0.0}

        n_total = len(details)
        mean_db = sum(x[3] for x in details) / n_total
        max_db = max(x[3] for x in details)

        out_count = sum(
            1 for (_, dl, dr, db) in details
            if dl > target_l or dr > target_r or db > target_b
        )
        out_rate = 100.0 * out_count / n_total

        core_notes = sum(1 for n in score.notes if n.role in ("melody", "bass"))
        add_notes = n_total - core_notes
        add_rate = 100.0 * add_notes / max(1, core_notes)

        return {
            "total_notes": n_total,
            "mean_DB": round(mean_db, 2),
            "max_DB": round(max_db, 2),
            "out_of_range_pct": round(out_rate, 1),
            "add_note_pct": round(add_rate, 1),
        }