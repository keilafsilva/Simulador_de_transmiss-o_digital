"""Cadeia completa: bits -> codificação de linha -> modulação -> canal -> demodulação -> decodificação."""
from .ascii_io import ascii_to_bits, bits_to_ascii
from .channel import awgn, burst_awgn
from .linecode import LINE_CODES
from .modulation import MODULATIONS

BURST_PADRAO = dict(p_gb=0.01, p_bg=0.1, penalty_db=12.0)


def run_chain(info_bits, line="none", mod="bpsk", ebn0_db=None, rng=None,
              channel="awgn", burst=None):
    """Retorna (bits recebidos, violações de linha). ebn0_db=None = canal ideal."""
    encode, decode, rate = LINE_CODES[line]
    m = MODULATIONS[mod]
    chips = encode(info_bits)
    simbolos, _ = m.modulate(chips)
    k_info = m.k * rate
    if ebn0_db is None:
        rx = simbolos
    elif channel == "awgn":
        rx = awgn(simbolos, ebn0_db, k_info, rng)
    elif channel == "burst":
        rx = burst_awgn(simbolos, ebn0_db, k_info, rng, **(burst or BURST_PADRAO))
    else:
        raise ValueError(channel)
    chips_rx = m.demodulate(rx, len(chips))
    return decode(chips_rx)


def run_message(texto, **kw):
    tx = ascii_to_bits(texto)
    rx, viol = run_chain(tx, **kw)
    return tx, rx, bits_to_ascii(rx), viol
