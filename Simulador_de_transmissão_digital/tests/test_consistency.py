"""Testes de consistência (rodar: python -m pytest -v)."""
import itertools

import numpy as np

from src.ascii_io import ascii_to_bits, bits_to_ascii
from src.channel import gilbert_elliott_states
from src.linecode import LINE_CODES
from src.metrics import ber
from src.modulation import MODULATIONS, theory_ber
from src.pipeline import run_chain, run_message

MSG = "Redes de Computadores - UNISINOS - Trabalho II"


def test_ascii_ida_e_volta():
    assert bits_to_ascii(ascii_to_bits(MSG)) == MSG
    assert ascii_to_bits("O").tolist() == [0, 1, 0, 0, 1, 1, 1, 1]


def test_codigos_de_linha_ida_e_volta():
    bits = np.random.default_rng(0).integers(0, 2, 1001).astype(np.uint8)
    for nome, (enc, dec, taxa) in LINE_CODES.items():
        chips = enc(bits)
        assert len(chips) == len(bits) / taxa
        out, viol = dec(chips)
        assert np.array_equal(out, bits) and viol == 0, nome


def test_bifase_mark_transicao_em_toda_borda():
    bits = np.random.default_rng(1).integers(0, 2, 500).astype(np.uint8)
    c = LINE_CODES["bifase_mark"][0](bits).reshape(-1, 2)
    assert np.all(c[1:, 0] != c[:-1, 1])


def test_constelacoes_energia_unitaria_e_gray():
    for nome, m in MODULATIONS.items():
        todos = np.array(list(itertools.product([0, 1], repeat=m.k)), dtype=np.uint8)
        simb, _ = m.modulate(todos.reshape(-1))
        assert abs(np.mean(np.abs(simb) ** 2) - 1) < 1e-12, nome
        assert np.array_equal(m.demodulate(simb, todos.size), todos.reshape(-1)), nome
        if m.k > 1:                       # Gray: vizinhos mais próximos diferem em 1 bit
            d = np.abs(simb[:, None] - simb[None, :]) + np.eye(len(simb)) * 99
            dmin = d.min()
            for i, j in zip(*np.where(np.isclose(d, dmin))):
                assert np.sum(todos[i] != todos[j]) == 1, (nome, i, j)


def test_canal_ideal_recupera_mensagem_em_todas_as_combinacoes():
    for line, mod in itertools.product(LINE_CODES, MODULATIONS):
        tx, rx, texto, viol = run_message(MSG, line=line, mod=mod, ebn0_db=None)
        assert texto == MSG and ber(tx, rx) == 0 and viol == 0, (line, mod)


def test_snr_alto_recupera_mensagem():
    rng = np.random.default_rng(3)
    for line, mod in itertools.product(LINE_CODES, MODULATIONS):
        _, _, texto, _ = run_message(MSG, line=line, mod=mod, ebn0_db=30, rng=rng)
        assert texto == MSG, (line, mod)


def test_ber_simulada_bate_com_a_teoria_awgn():
    rng = np.random.default_rng(42)
    bits = rng.integers(0, 2, 400_000).astype(np.uint8)
    for mod in MODULATIONS:
        rx, _ = run_chain(bits, line="none", mod=mod, ebn0_db=6, rng=rng)
        sim, teo = ber(bits, rx), theory_ber(mod, 6)[0]
        assert abs(sim - teo) / teo < 0.10, (mod, sim, teo)


def test_rajadas_fracao_de_tempo_no_estado_ruim():
    rng = np.random.default_rng(5)
    est = gilbert_elliott_states(500_000, 0.01, 0.1, rng)
    assert abs(est.mean() - 0.01 / 0.11) < 0.02
