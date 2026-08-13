"""Geração da planilha de triagem."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font

from .processo import Resultado

SAIDA = Path("saida")

COLUNAS = [
    ("Processo", "processo", 24),
    ("Interessado", "interessado", 42),
    ("Autuação", "autuacao", 12),
    ("Último laudo", "documento", 28),
    ("Nº SEI", "numero_sei", 14),
    ("Unidade que incluiu", "unidade", 28),
    ("Docs", "total_documentos", 7),
    ("Observação", "observacao", 26),
]


def exportar(resultados: list[Resultado], prefixo: str = "laudos") -> Path:
    """Grava a planilha. `prefixo` distingue a definitiva de uma prévia — nomes
    parecidos já fizeram a planilha errada ser aberta."""
    SAIDA.mkdir(exist_ok=True)
    destino = SAIDA / f"{prefixo}_{datetime.now():%Y-%m-%d_%H%M}.xlsx"

    planilha = Workbook()
    aba = planilha.active
    aba.title = "Laudos"

    aba.append([titulo for titulo, _, _ in COLUNAS])
    for celula in aba[1]:
        celula.font = Font(bold=True)
        celula.alignment = Alignment(horizontal="center")

    for resultado in resultados:
        aba.append([getattr(resultado, campo) for _, campo, _ in COLUNAS])

    for indice, (_, _, largura) in enumerate(COLUNAS, start=1):
        aba.column_dimensions[aba.cell(row=1, column=indice).column_letter].width = largura

    aba.freeze_panes = "A2"
    aba.auto_filter.ref = aba.dimensions
    planilha.save(destino)
    return destino
