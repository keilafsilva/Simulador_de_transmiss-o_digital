"""Etapas 3 e 5: modulação (bits -> símbolos complexos I+jQ) e demodulação por mínima distância.
Todas com mapeamento Gray e energia média por símbolo normalizada (Es = 1).
"""
from math import erfc, sqrt

import numpy as np

_GRAY2 = np.array([[0, 0], [0, 1], [1, 1], [1, 0]], dtype=np.uint8)   # nível 0..3 -> bits
_NIVEL = np.array([-3, -1, 3, 1])                                      # índice 2*b0+b1 -> nível


class Modulation:
    def __init__(self, name, k):
        self.name, self.k = name, k          # k = bits por símbolo = eficiência espectral nominal

    def modulate(self, bits):
        b = np.asarray(bits, dtype=np.uint8)
        pad = (-len(b)) % self.k
        if pad:
            b = np.concatenate([b, np.zeros(pad, dtype=np.uint8)])
        return self._map(b.reshape(-1, self.k)), pad

    def demodulate(self, symbols, n_bits):
        return self._demap(np.asarray(symbols)).reshape(-1)[:n_bits].astype(np.uint8)


class BPSK(Modulation):
    def __init__(self):
        super().__init__("bpsk", 1)

    def _map(self, b):
        return (2.0 * b[:, 0] - 1.0).astype(complex)                   # 0 -> -1, 1 -> +1

    def _demap(self, s):
        return (s.real > 0).astype(np.uint8)[:, None]


class QPSK(Modulation):
    def __init__(self):
        super().__init__("qpsk", 2)

    def _map(self, b):                                                  # 0 -> +, 1 -> -
        return ((1.0 - 2.0 * b[:, 0]) + 1j * (1.0 - 2.0 * b[:, 1])) / sqrt(2)

    def _demap(self, s):
        return np.stack([(s.real < 0), (s.imag < 0)], axis=1).astype(np.uint8)


class QAM16(Modulation):
    def __init__(self):
        super().__init__("qam16", 4)

    def _map(self, b):
        i = _NIVEL[2 * b[:, 0] + b[:, 1]]
        q = _NIVEL[2 * b[:, 2] + b[:, 3]]
        return (i + 1j * q) / sqrt(10)

    @staticmethod
    def _eixo(x):
        idx = np.digitize(x * sqrt(10), [-2, 0, 2])                     # limiares de decisão
        return _GRAY2[idx]

    def _demap(self, s):
        return np.hstack([self._eixo(s.real), self._eixo(s.imag)])


MODULATIONS = {"bpsk": BPSK(), "qpsk": QPSK(), "qam16": QAM16()}


def qfunc(x):
    return 0.5 * erfc(x / sqrt(2))


def theory_ber(mod, ebn0_db):
    """BER teórica em AWGN (Gray): BPSK/QPSK = Q(sqrt(2Eb/N0)); 16-QAM ~ 0,75 Q(sqrt(0,8Eb/N0))."""
    g = 10 ** (np.atleast_1d(np.asarray(ebn0_db, dtype=float)) / 10)
    if mod in ("bpsk", "qpsk"):
        return np.array([qfunc(sqrt(2 * x)) for x in g])
    return np.array([0.75 * qfunc(sqrt(0.8 * x)) for x in g])
