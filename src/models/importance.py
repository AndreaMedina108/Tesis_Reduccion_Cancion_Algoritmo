from .score import Note


def compute_musical_importance(note: Note, a: float = 0.25) -> float:
    """
    Calcula h(m) = I(m in M) + I(m in B) + a * Mult(m) (Ec. 13, Nakamura & Yoshii 2018).
    Valores altos indican notas estructurales que el optimizador debe preservar.
    """
    is_melody = 1.0 if note.role == "melody" else 0.0
    is_bass = 1.0 if note.role == "bass" else 0.0
    return is_melody + is_bass + a * note.multiplicity