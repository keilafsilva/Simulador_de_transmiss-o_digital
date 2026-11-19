"""Etapas 2 e 6: codificação de linha. Saída = 'chips' (meios-bits) binários,
para poderem ser entregues a qualquer modulação binária/M-ária.

Convenções adotadas:
  Manchester  : bit 1 = chips 01 (subida no meio do bit); bit 0 = chips 10 (descida).
  Bifase Mark : sempre há transição no INÍCIO do bit; o bit 1 tem transição extra no MEIO.
                Nível anterior ao primeiro bit = 0.
Todas as funções de decodificação retornam (bits, violacoes).
"""
import numpy as np


def identity_encode(bits):
    return np.asarray(bits, dtype=np.uint8)


def identity_decode(chips):
    return np.asarray(chips, dtype=np.uint8), 0


def manchester_encode(bits):
    b = np.asarray(bits, dtype=np.uint8)
    chips = np.empty(2 * len(b), dtype=np.uint8)
    chips[0::2] = 1 - b
    chips[1::2] = b
    return chips


def manchester_decode(chips):
    c = np.asarray(chips, dtype=np.uint8).reshape(-1, 2)
    violacoes = int(np.sum(c[:, 0] == c[:, 1]))          # 00 ou 11 não existem no código
    bits = ((c[:, 0] == 0) & (c[:, 1] == 1)).astype(np.uint8)   # na violação assume-se bit 0
    return bits, violacoes


def bifase_mark_encode(bits):
    b = np.asarray(bits, dtype=np.uint8)
    nivel_final = np.cumsum(1 - b) % 2                    # nível ao fim de cada bit
    anterior = np.concatenate(([0], nivel_final[:-1])).astype(np.uint8)
    primeiro = 1 - anterior                               # inversão no início do bit
    segundo = primeiro ^ b                                # bit 1 inverte de novo no meio
    chips = np.empty(2 * len(b), dtype=np.uint8)
    chips[0::2], chips[1::2] = primeiro, segundo
    return chips


def bifase_mark_decode(chips):
    c = np.asarray(chips, dtype=np.uint8).reshape(-1, 2)
    bits = (c[:, 0] != c[:, 1]).astype(np.uint8)          # chips diferentes -> bit 1
    violacoes = int(np.sum(c[1:, 0] == c[:-1, 1]))        # deveria sempre haver transição na borda
    return bits, violacoes


# nome -> (codificar, decodificar, taxa do código = bits de informação / chips)
LINE_CODES = {
    "none": (identity_encode, identity_decode, 1.0),
    "manchester": (manchester_encode, manchester_decode, 0.5),
    "bifase_mark": (bifase_mark_encode, bifase_mark_decode, 0.5),
}
