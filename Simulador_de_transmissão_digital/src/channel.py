"""Etapa 4: canal. Eb/N0 é definido por BIT DE INFORMAÇÃO:
Eb = Es / (bits de informação por símbolo) e sigma por dimensão = sqrt(N0/2), com Es = 1.
Por isso a codificação de linha (taxa 1/2) custa ~3 dB por chip.
"""
import numpy as np


def sigma_from_ebn0(ebn0_db, k_info):
    eb = 1.0 / k_info
    n0 = eb / (10 ** (ebn0_db / 10))
    return np.sqrt(n0 / 2)


def awgn(symbols, ebn0_db, k_info, rng):
    s = sigma_from_ebn0(ebn0_db, k_info)
    ruido = rng.normal(0, s, symbols.shape) + 1j * rng.normal(0, s, symbols.shape)
    return symbols + ruido


def gilbert_elliott_states(n, p_gb, p_bg, rng):
    """Cadeia de Markov de 2 estados (bom/ruim). True = estado ruim. Início na distribuição estacionária."""
    ruim = rng.random() < p_gb / (p_gb + p_bg)
    estados = np.zeros(n, dtype=bool)
    pos = 0
    while pos < n:
        dur = rng.geometric(p_bg if ruim else p_gb)
        if ruim:
            estados[pos:pos + dur] = True
        pos += dur
        ruim = not ruim
    return estados


def burst_awgn(symbols, ebn0_db, k_info, rng, p_gb=0.01, p_bg=0.1, penalty_db=12.0):
    """AWGN com rajadas: no estado ruim o desvio do ruído é multiplicado por 10^(penalty/20)."""
    s = sigma_from_ebn0(ebn0_db, k_info)
    ruim = gilbert_elliott_states(len(symbols), p_gb, p_bg, rng)
    sigma = np.where(ruim, s * 10 ** (penalty_db / 20), s)
    ruido = rng.normal(0, 1, symbols.shape) * sigma + 1j * rng.normal(0, 1, symbols.shape) * sigma
    return symbols + ruido
