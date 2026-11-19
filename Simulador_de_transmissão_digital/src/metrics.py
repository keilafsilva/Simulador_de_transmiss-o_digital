"""Etapa 7: métricas."""
import numpy as np


def ber(tx, rx):
    tx, rx = np.asarray(tx), np.asarray(rx)
    return float(np.mean(tx != rx))


def error_positions(tx, rx):
    return np.flatnonzero(np.asarray(tx) != np.asarray(rx))


def spectral_efficiency(bits_per_symbol, code_rate=1.0):
    """Eficiência espectral nominal (bit/s/Hz): filtro ideal, banda = taxa de símbolos."""
    return bits_per_symbol * code_rate
