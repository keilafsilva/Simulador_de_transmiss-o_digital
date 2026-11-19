"""Etapa 1 e 7: texto ASCII <-> bits."""
import numpy as np


def ascii_to_bits(texto: str) -> np.ndarray:
    """Cada caractere vira 8 bits (MSB primeiro)."""
    dados = np.frombuffer(texto.encode("ascii"), dtype=np.uint8)
    return np.unpackbits(dados)


def bits_to_ascii(bits) -> str:
    """Agrupa de 8 em 8 bits. Bytes fora de 32..126 (corrompidos) aparecem como '?'."""
    b = np.asarray(bits, dtype=np.uint8)
    b = b[: len(b) // 8 * 8]
    return "".join(chr(c) if 32 <= c < 127 else "?" for c in np.packbits(b).tobytes())
