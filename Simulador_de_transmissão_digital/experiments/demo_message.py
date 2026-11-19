"""Experimento C: mensagem ASCII ponta a ponta, com identificação dos bits incorretos.
Rodar da raiz:  python -m experiments.demo_message
Saída: tela e results/demo_mensagem.txt"""
from pathlib import Path

import numpy as np

from src.metrics import ber, error_positions
from src.pipeline import run_message

MSG = "Redes de Computadores - UNISINOS - Trabalho II"
SEED = 2026


def relatorio(tx, rx, texto):
    """Lista cada bit incorreto: posição do bit, caractere afetado e como ele chegou."""
    pos = error_positions(tx, rx)
    linhas = []
    for c in sorted({int(p) // 8 for p in pos}):
        bits_c = [int(p) % 8 for p in pos if int(p) // 8 == c]
        linhas.append(f"      caractere {c:2d}: '{MSG[c]}' -> '{texto[c]}'  (bits errados no byte: {bits_c})")
    return pos, linhas


def main():
    rng = np.random.default_rng(SEED)
    out = [f"Mensagem enviada: |{MSG}|  ({len(MSG) * 8} bits)", f"Semente: {SEED}", ""]

    out.append("1) Teste de consistência: canal ideal (sem ruído), todas as combinações")
    for line in ("none", "manchester", "bifase_mark"):
        for mod in ("bpsk", "qpsk", "qam16"):
            tx, rx, texto, viol = run_message(MSG, line=line, mod=mod, ebn0_db=None)
            ok = "OK" if texto == MSG and ber(tx, rx) == 0 else "FALHOU"
            out.append(f"   {line:12s} + {mod:5s}: BER = {ber(tx, rx):.0f}, mensagem idêntica: {ok}")

    out.append("")
    out.append("2) Canal com ruído (sem codificação de linha)")
    for canal in ("awgn", "burst"):
        out.append(f"   --- canal: {canal} ---")
        for mod in ("bpsk", "qpsk", "qam16"):
            for eb in (4, 8, 12):
                tx, rx, texto, _ = run_message(MSG, line="none", mod=mod, ebn0_db=eb, rng=rng, channel=canal)
                pos, det = relatorio(tx, rx, texto)
                out.append(f"   {mod:5s} Eb/N0={eb:2d} dB  BER={ber(tx, rx):.4f}  erros={len(pos):3d}  |{texto}|")
                out.extend(det[:6])
                if len(det) > 6:
                    out.append(f"      ... e mais {len(det) - 6} caracteres afetados")

    texto_final = "\n".join(out)
    print(texto_final)
    Path("results").mkdir(exist_ok=True)
    Path("results/demo_mensagem.txt").write_text(texto_final + "\n")


if __name__ == "__main__":
    main()
