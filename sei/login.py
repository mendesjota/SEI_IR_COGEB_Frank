"""Autenticação no SIP e o modal de senha de credencial do SEI."""

from __future__ import annotations

from playwright.async_api import Page
from playwright.async_api import TimeoutError as ErroDeTempo

from .config import Config

MODAL_CREDENCIAL = "iframe[name='modal-frame']"


async def login(page: Page, cfg: Config) -> None:
    await page.goto(cfg.url_login)
    await page.get_by_role("textbox", name="Usuário").fill(cfg.usuario)
    await page.get_by_role("textbox", name="Senha").fill(cfg.senha)
    await selecionar_orgao(page, cfg.orgao)
    await page.get_by_role("button", name="ACESSAR").click()
    await page.wait_for_load_state()

    if "login.php" in page.url:
        aviso = page.locator("#txaInfraValidacao")
        motivo = (await aviso.input_value()) if await aviso.count() else "motivo desconhecido"
        raise RuntimeError(f"Login recusado pelo SIP: {motivo}")


async def selecionar_orgao(page: Page, orgao: str) -> None:
    """Seleciona o órgão aceitando tanto o value do option quanto o texto visível.

    O codegen gravou select_option("26") — o value —, mas o .env pode guardar a
    sigla ("IPREV"). Tentamos as duas leituras antes de desistir.
    """
    combo = page.locator("#selOrgao")
    for criterio in ({"value": orgao}, {"label": orgao}):
        try:
            await combo.select_option(**criterio, timeout=5000)
            return
        except Exception:
            continue

    opcoes = await combo.locator("option").all_inner_texts()
    raise RuntimeError(
        f"SEI_Orgao={orgao!r} não corresponde a nenhuma opção do combo. "
        f"Opções disponíveis: {opcoes}"
    )


async def resolver_modal_credencial(
    page: Page, senha: str, tentativas: int = 3, timeout: int = 3000
) -> int:
    """Responde o modal de senha de credencial, se ele estiver na tela.

    Idempotente de propósito: sem modal visível a função apenas retorna. O SEI
    reabre esse modal a cada aba nova e, às vezes, duas vezes seguidas — daí o
    laço. Devolve quantas vezes precisou responder.
    """
    resolvidos = 0
    for tentativa in range(tentativas):
        # Só a primeira espera vale o timeout cheio: se o SEI for reabrir o modal,
        # ele reabre imediatamente. Esperar 3s por um modal que não vem custava
        # 4s por processo — 97% do tempo de extração.
        espera = timeout if tentativa == 0 else 700

        modal = page.locator(MODAL_CREDENCIAL)
        try:
            await modal.wait_for(state="visible", timeout=espera)
            campo = modal.content_frame.get_by_role("textbox", name="Senha:")
            await campo.wait_for(state="visible", timeout=espera)
        except ErroDeTempo:
            break

        await campo.fill(senha)
        await modal.content_frame.get_by_role("button", name="Acessar").click()
        resolvidos += 1

        # Aguarda o modal sumir de fato, em vez de dormir um tempo fixo.
        try:
            await modal.wait_for(state="hidden", timeout=10000)
        except ErroDeTempo:
            pass

    return resolvidos
