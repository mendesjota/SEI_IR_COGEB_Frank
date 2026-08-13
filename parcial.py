"""Gera a planilha com o que já foi extraído até agora.

    uv run parcial.py

Lê apenas saida/checkpoint.jsonl, sem tocar no navegador — pode rodar com a
varredura em andamento, quantas vezes quiser.
"""

from sei import checkpoint
from sei.export import exportar

if __name__ == "__main__":
    resultados = checkpoint.carregar()
    if not resultados:
        raise SystemExit("nada extraído ainda (saida/checkpoint.jsonl vazio)")

    com_laudo = sum(1 for r in resultados if r.numero_sei)
    destino = exportar(resultados, prefixo="PARCIAL")
    print(f"{len(resultados)} processos | {com_laudo} com laudo")
    print(f"planilha: {destino}")
