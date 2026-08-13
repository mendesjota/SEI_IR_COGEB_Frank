"""Codegen original do Playwright, mantido só como referência histórica.

NÃO roda como está e não deve ser corrigido: o robô de verdade está em app.py.

Sanitizado. O codegen grava tudo que foi clicado na gravação — inclusive o
usuário de login, os números dos processos abertos e, no aria-label das
células da fila, o NOME DO INTERESSADO. Como a fila é de Isenção de IR (que
se concede por doença grave), nome + tipo de processo é dado de saúde.
Os valores abaixo foram trocados por marcadores; ao regravar um codegen,
sanitize antes de salvar no repositório.
"""

import re
from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://sip.df.gov.br/sip/login.php?sigla_orgao_sistema=GDF&sigla_sistema=SEI&infra_url=L3NlaS8=")
    page.get_by_role("textbox", name="Usuário").click()
    page.get_by_role("textbox", name="Usuário").fill("SEI_USUARIO")
    page.get_by_role("textbox", name="Senha").click()
    page.get_by_role("textbox", name="Senha").fill("SEI_SENHA")
    page.locator("#selOrgao").select_option("26")
    page.get_by_role("button", name="ACESSAR").click()
    page.get_by_role("link", name="IPREV/DIPREV/COGEB/GEMF").click()
    page.locator("#divInfraAreaTabela").get_by_text("IPREV/DIPREV/COGEB/GEMF", exact=True).click()
    page.get_by_role("link", name="IPREV/DIPREV/COGEB/GEMF").click()
    page.get_by_role("link", name="Pessoal: Acerto de Contas / auxílio funeral").click()
    page.get_by_text("-00000000/0000-00").click()
    page.locator("#lnkRecebidosProximaPaginaInferior").click()
    page.locator("#lnkRecebidosPaginaAnteriorInferior").click()
    page.get_by_role("link", name="Processos com Credencial de").click()
    page.locator("iframe[name=\"modal-frame\"]").content_frame.get_by_role("textbox", name="Senha:").fill("SEI_SENHA_CREDENCIAL")
    page.locator("iframe[name=\"modal-frame\"]").content_frame.get_by_role("button", name="Acessar").click()
    with page.expect_popup() as page1_info:
        page.get_by_text("-00000000/0000-00").click()
    page1 = page1_info.value
    page1.locator("iframe[name=\"modal-frame\"]").content_frame.get_by_role("textbox", name="Senha:").click()
    page1.locator("iframe[name=\"modal-frame\"]").content_frame.get_by_role("textbox", name="Senha:").fill("SEI_SENHA_CREDENCIAL")
    page1.locator("iframe[name=\"modal-frame\"]").content_frame.get_by_role("button", name="Acessar").click()
    page1.locator("iframe[name=\"modal-frame\"]").content_frame.get_by_role("textbox", name="Senha:").click()
    page1.locator("iframe[name=\"modal-frame\"]").content_frame.get_by_role("textbox", name="Senha:").fill("SEI_SENHA_CREDENCIAL")
    page1.locator("iframe[name=\"modal-frame\"]").content_frame.get_by_role("button", name="Acessar").click()
    page1.get_by_role("link", name="IPREV/DIPREV/COGEB/GEMF").click()
    page1.locator("#divInfraAreaTabela").get_by_text("IPREV/DIPREV/COGEB/GEMF", exact=True).click()
    page1.locator(".nav-item.px-1.d-none").click()
    page1.get_by_role("link", name="Processos com Credencial de").click()
    page1.locator("iframe[name=\"modal-frame\"]").content_frame.get_by_role("textbox", name="Senha:").click()
    page1.locator("iframe[name=\"modal-frame\"]").content_frame.get_by_role("textbox", name="Senha:").fill("SEI_SENHA_CREDENCIAL")
    page1.locator("iframe[name=\"modal-frame\"]").content_frame.get_by_role("button", name="Acessar").click()
    page1.locator("#lnkInfraProximaPaginaInferior").click()
    page1.locator("#lnkInfraUltimaPaginaInferior").click()
    with page1.expect_popup() as page2_info:
        page1.get_by_role("cell", name="Pessoal: Isenção de Imposto de Renda / NOME DO INTERESSADO").click()
    page2 = page2_info.value
    page2.locator("iframe[name=\"modal-frame\"]").content_frame.get_by_role("textbox", name="Senha:").click()
    page2.locator("iframe[name=\"modal-frame\"]").content_frame.get_by_role("textbox", name="Senha:").fill("SEI_SENHA_CREDENCIAL")
    page2.locator("iframe[name=\"modal-frame\"]").content_frame.get_by_role("button", name="Acessar").click()
    page2.locator("iframe[name=\"ifrArvore\"]").content_frame.get_by_role("link", name="Laudo Técnico (0000000)").click()
    page2.close()
    page1.close()
    page.close()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
