from dataclasses import dataclass, replace
from typing import List, Literal

HandType = Literal["L", "R"]
RoleType = Literal["melody", "bass", "harmony"]


@dataclass
class Note:
    pitch: int          # Altura MIDI (ej. 60 = C4, 69 = A4)
    onset: float        # Tiempo de inicio en segundos
    duration: float     # Duración en segundos
    role: RoleType      # 'melody' (M), 'bass' (B) o 'harmony' (relleno)
    hand: HandType = "R"
    multiplicity: int = 0  # Cuántos instrumentos duplican esta nota en el ensamble

    def clone(self, **kwargs) -> "Note":
        return replace(self, **kwargs)


class Score:
    def __init__(self, notes: List[Note], title: str = "Score"):
        # Ordenar cronológicamente por inicio y de grave a agudo
        self.notes: List[Note] = sorted(notes, key=lambda n: (round(n.onset, 4), n.pitch))
        self.title = title

    def get_hand_notes(self, hand: HandType) -> List[Note]:
        return [n for n in self.notes if n.hand == hand]

    def total_duration(self) -> float:
        if not self.notes:
            return 0.0
        return max(n.onset + n.duration for n in self.notes)

    def __len__(self) -> int:
        return len(self.notes)