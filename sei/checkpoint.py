"""Checkpoint em JSON Lines, para retomar uma varredura de horas."""

from __future__ import annotations

import json
from pathlib import Path

from .processo import Resultado

SAIDA = Path("saida")
ARQUIVO = SAIDA / "checkpoint.jsonl"


def carregar() -> list[Resultado]:
    """Lê o que já foi extraído. Linhas corrompidas (queda no meio da escrita)
    são descartadas em silêncio — o processo será refeito."""
    if not ARQUIVO.exists():
        return []

    resultados = []
    for linha in ARQUIVO.read_text(encoding="utf-8").splitlines():
        if not linha.strip():
            continue
        try:
            resultados.append(Resultado(**json.loads(linha)))
        except (json.JSONDecodeError, TypeError):
            continue
    return resultados


def gravar(resultado: Resultado) -> None:
    SAIDA.mkdir(exist_ok=True)
    with ARQUIVO.open("a", encoding="utf-8") as arquivo:
        arquivo.write(json.dumps(resultado.como_dict(), ensure_ascii=False) + "\n")
