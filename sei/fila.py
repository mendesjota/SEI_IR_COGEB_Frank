"""Fila 'Processos com Credencial de Segurança': paginação e filtro.

A coleta é feita página a página, e cada processo é aberto logo em seguida.
Não dá para juntar todas as URLs antes: o `infra_hash` das URLs vale só para a
sessão que as gerou — reaproveitar um hash de outra sessão não apenas falha,
como derruba a sessão atual (o SIP responde "Hash inválido" e desloga).
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from urllib.parse import urljoin

from playwright.async_api import Page

from .config import Config
from .login import resolver_modal_credencial

LINK_PROCESSO = 'a[href*="id_procedimento"]'
PROXIMA_PAGINA = "#lnkInfraProximaPaginaInferior"
TABELA = "#divInfraAreaTabela table"
TENTATIVAS_PAGINACAO = 3


@dataclass(frozen=True)
class ItemFila:
    processo: str
    tipo: str
    especificacao: str
    autuacao: str
    url: str


def normalizar(texto: str) -> str:
    """Minúsculas e sem acentos, para comparar tipo de processo com segurança."""
    sem_acento = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in sem_acento if not unicodedata.combining(c)).lower()


def eh_isencao(tipo: str) -> bool:
    t = normalizar(tipo)
    return "isencao" in t and "imposto de renda" in t


def separar_especificacao(rotulo: str) -> tuple[str, str]:
    """O aria-label traz "Tipo / Especificação" — e a especificação às vezes é o
    nome do interessado. Fora isso, o interessado não aparece em lugar nenhum da
    fila nem da página do processo."""
    tipo, separador, especificacao = rotulo.partition(" / ")
    return (tipo.strip(), especificacao.strip()) if separador else (rotulo.strip(), "")


async def abrir_fila(page: Page, cfg: Config) -> None:
    await page.get_by_role("link", name="Processos com Credencial de").click()
    await resolver_modal_credencial(page, cfg.senha_credencial)
    await page.wait_for_load_state()


async def total_de_registros(page: Page) -> int:
    caption = page.locator(f"{TABELA} caption").first
    if not await caption.count():
        return 0
    achado = re.search(r"\((\d+)\s+registros", await caption.inner_text())
    return int(achado.group(1)) if achado else 0


async def itens_da_pagina(page: Page, apenas_isencao: bool = True) -> list[ItemFila]:
    """Lê as linhas da página atual da fila. Não abre nada."""
    itens: list[ItemFila] = []
    linhas = page.locator(f"{TABELA} tr")

    for i in range(1, await linhas.count()):
        linha = linhas.nth(i)
        link = linha.locator(LINK_PROCESSO).first
        if not await link.count():
            continue

        rotulo = (await link.get_attribute("aria-label") or "").strip()
        tipo, especificacao = separar_especificacao(rotulo)
        if apenas_isencao and not eh_isencao(tipo):
            continue

        celulas = await linha.locator("td").all_inner_texts()
        itens.append(
            ItemFila(
                processo=(await link.inner_text()).strip(),
                tipo=tipo,
                especificacao=especificacao,
                autuacao=celulas[3].strip() if len(celulas) > 3 else "",
                url=urljoin(page.url, await link.get_attribute("href") or ""),
            )
        )

    return itens


async def proxima_pagina(page: Page, cfg: Config) -> bool:
    """Avança uma página. Devolve False quando não há mais — ou quando o SEI
    deixa de responder.

    Numa varredura de 138 páginas o clique de paginação chega a travar mesmo com
    o link visível e habilitado (sessão longa). Como já são horas de trabalho no
    checkpoint, aqui se insiste algumas vezes e, no limite, encerra a varredura
    em vez de deixar a exceção subir.
    """
    proxima = page.locator(PROXIMA_PAGINA)
    if not await proxima.count() or not await proxima.is_visible():
        return False

    for tentativa in range(1, TENTATIVAS_PAGINACAO + 1):
        try:
            await proxima.click(timeout=20000)
            await resolver_modal_credencial(page, cfg.senha_credencial)
            await page.wait_for_load_state()
            return True
        except Exception as erro:
            print(
                f"  !! paginação falhou ({tentativa}/{TENTATIVAS_PAGINACAO}): "
                f"{type(erro).__name__}"
            )
            if tentativa == TENTATIVAS_PAGINACAO:
                return False
            await page.wait_for_timeout(3000 * tentativa)
            try:
                await page.reload(timeout=30000)
                await resolver_modal_credencial(page, cfg.senha_credencial)
            except Exception:
                return False

    return False
