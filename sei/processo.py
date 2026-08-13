"""Extração do último laudo na árvore de documentos do processo."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from urllib.parse import urljoin

from playwright.async_api import Page

from .config import Config
from .fila import ItemFila
from .login import resolver_modal_credencial

# "Requerimento (200000000)" e também "Despacho 200000001" — documentos gerados
# no SEI aparecem sem parênteses. O número tem 5+ dígitos, o que descarta o nó
# raiz do processo ("00000-00000000/0000-00" termina em dois dígitos).
DOCUMENTO = re.compile(r"^(?P<nome>.*?)\s*\(?(?P<numero>\d{5,})\)?$")
# Sigla da unidade, no link imediatamente após o documento. Separador costuma
# ser "/" (IPREV/DIPREV/COCAT/GEAS) mas também aparece "_" (SEEC_SUBSAUDE/COPEM
# /DIPEM) — exigir só a barra deixava 733 laudos sem unidade na planilha.
SIGLA_UNIDADE = re.compile(r"^[A-ZÇÃÕÁÉÍÓÚÂÊÔ0-9_]+([/_][A-ZÇÃÕ0-9_\-]+)+$")

ARVORE = "iframe[name='ifrArvore']"
CONTEUDO = "iframe[name='ifrConteudoVisualizacao']"
# O interessado nao existe em nenhum frame da pagina do processo: fica na tela
# "Consultar Processo", alcancada por este botao — cujo href ja traz um
# infra_hash valido gerado pelo servidor (montar a URL na mao derruba a sessao).
BOTAO_CONSULTAR = 'a:has(img[alt="Consultar Processo"])'
SELECT_INTERESSADOS = "#selInteressadosProcedimento option"
# O SEI serializa requisições da mesma sessão e ocasionalmente engasga; sem
# repetir, o processo entraria na planilha sem laudo mesmo tendo um.
TENTATIVAS = 3


@dataclass
class Resultado:
    processo: str
    especificacao: str
    autuacao: str
    interessado: str = ""
    documento: str = ""
    numero_sei: str = ""
    unidade: str = ""
    total_documentos: int = 0
    observacao: str = ""

    def como_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class Documento:
    nome: str
    numero: str
    unidade: str


def documentos_da_arvore(textos: list[str]) -> list[Documento]:
    """Converte os textos dos links da árvore em documentos.

    A árvore alterna documento e unidade: o link seguinte a cada documento traz
    a sigla da área que o incluiu — é daí que sai a "área que adicionou".
    """
    documentos = []
    for i, texto in enumerate(textos):
        casou = DOCUMENTO.match(texto)
        if not texto or not casou:
            continue

        unidade = ""
        for j in range(i + 1, min(i + 4, len(textos))):
            if SIGLA_UNIDADE.match(textos[j]):
                unidade = textos[j]
                break

        documentos.append(
            Documento(casou.group("nome"), casou.group("numero"), unidade)
        )
    return documentos


def ultimo_laudo(documentos: list[Documento]) -> Documento | None:
    """O último laudo da árvore, lendo de baixo para cima."""
    laudos = [d for d in documentos if "laudo" in d.nome.lower()]
    return laudos[-1] if laudos else None


async def extrair_interessado(aba: Page, cfg: Config, timeout: int = 3500) -> str:
    """Nome(s) do interessado, pela tela 'Consultar Processo'.

    Cobertura medida em amostra de 36 processos espalhados pela fila: 75%. Nos
    demais o botão não existe no HTML (o acesso por credencial não dá direito à
    tela de consulta) ou a tela abre sem o select. Não é falha recuperável —
    devolve string vazia e segue.

    Navega a própria aba para fora da tela do processo, então só pode ser
    chamada DEPOIS de a árvore já ter sido lida.

    O timeout é curto de propósito: quando o botão existe, ele já está no DOM, e
    a espera só é paga por quem não tem — o que é 25% dos casos e domina o custo.
    """
    botao = aba.frame_locator(CONTEUDO).locator(BOTAO_CONSULTAR).first
    await botao.wait_for(state="attached", timeout=timeout)

    href = await botao.get_attribute("href")
    if not href:
        return ""

    # Base é aba.url, não a url do frame: o frame pode estar em about:blank e o
    # urljoin produziria uma URL inválida, levando o goto para lugar nenhum.
    await aba.goto(urljoin(aba.url, href), timeout=30000)
    await resolver_modal_credencial(aba, cfg.senha_credencial)

    opcoes = aba.locator(SELECT_INTERESSADOS)
    await opcoes.first.wait_for(state="attached", timeout=timeout)
    nomes = [t.strip() for t in await opcoes.all_inner_texts() if t.strip()]
    return " ; ".join(nomes)


async def extrair(aba: Page, item: ItemFila, cfg: Config) -> Resultado:
    """Abre o processo numa aba e devolve o último laudo encontrado.

    Nunca levanta: falhas viram texto na coluna Observação, para que um processo
    problemático não derrube uma varredura de horas.
    """
    resultado = Resultado(
        processo=item.processo,
        especificacao=item.especificacao,
        autuacao=item.autuacao,
    )

    textos: list[str] = []
    for tentativa in range(1, TENTATIVAS + 1):
        try:
            await aba.goto(item.url, timeout=60000)
            await resolver_modal_credencial(aba, cfg.senha_credencial)

            links = aba.frame_locator(ARVORE).get_by_role("link")
            # all_inner_texts() não espera: sem este wait ele devolve [] em silêncio.
            await links.first.wait_for(state="attached", timeout=45000)
            textos = [t.strip().replace("\n", " ") for t in await links.all_inner_texts()]
            break
        except Exception as erro:
            if tentativa == TENTATIVAS:
                resultado.observacao = (
                    f"falha ao abrir após {TENTATIVAS} tentativas: {type(erro).__name__}"
                )
                return resultado
            await aba.wait_for_timeout(1500 * tentativa)

    # Falhar aqui não pode custar o laudo, que é o dado principal — e em 25% dos
    # processos o interessado é mesmo inacessível.
    try:
        resultado.interessado = await extrair_interessado(aba, cfg)
    except Exception:
        resultado.interessado = ""

    documentos = documentos_da_arvore(textos)
    resultado.total_documentos = len(documentos)

    laudo = ultimo_laudo(documentos)
    if laudo is None:
        resultado.observacao = "sem laudo na árvore"
        return resultado

    resultado.documento = laudo.nome
    resultado.numero_sei = laudo.numero
    resultado.unidade = laudo.unidade
    return resultado
