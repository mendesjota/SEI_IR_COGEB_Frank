"""Raspagem do último laudo dos processos de Isenção de IR no SEI-DF.

Uso:
    uv run app.py

Controles pelo .env: HEADLESS, ABAS, LIMITE.
A varredura completa leva horas; o progresso vai para saida/checkpoint.jsonl e
a execução pode ser interrompida e retomada sem refazer o que já foi extraído.
"""

from __future__ import annotations

import asyncio
import time

from playwright.async_api import async_playwright

from sei import checkpoint
from sei.config import Config
from sei.export import exportar
from sei.fila import abrir_fila, itens_da_pagina, proxima_pagina, total_de_registros
from sei.login import login
from sei.processo import extrair


def em_lotes(itens: list, tamanho: int):
    for inicio in range(0, len(itens), tamanho):
        yield itens[inicio : inicio + tamanho]


async def main() -> None:
    cfg = Config.carregar()
    inicio = time.time()

    resultados = checkpoint.carregar()
    concluidos = {r.processo for r in resultados}
    if concluidos:
        print(f"retomando: {len(concluidos)} processos já extraídos\n")

    try:
        await varrer(cfg, resultados, concluidos, inicio)
    except KeyboardInterrupt:
        print("\ninterrompido pelo usuário")
    except Exception as erro:
        # Depois de horas de varredura, uma falha no fim não pode custar a
        # planilha: o que está no checkpoint vira arquivo de qualquer forma.
        print(f"\nvarredura interrompida por {type(erro).__name__}: {erro}")

    resultados = checkpoint.carregar()
    finalizar(resultados, inicio)


async def varrer(cfg: Config, resultados: list, concluidos: set, inicio: float) -> None:
    novos = 0
    async with async_playwright() as pw:
        navegador = await pw.chromium.launch(headless=cfg.headless)
        contexto = await navegador.new_context()

        fila = await contexto.new_page()
        await login(fila, cfg)
        await abrir_fila(fila, cfg)

        total = await total_de_registros(fila)
        paginas = (total + 49) // 50 if total else 1
        print(f"fila com {total} processos (~{paginas} páginas), {cfg.abas} abas\n")

        # As abas ficam abertas a varredura inteira: criar e fechar por processo
        # custaria mais que a própria navegação.
        abas = [await contexto.new_page() for _ in range(cfg.abas)]

        pagina = 1
        while True:
            itens = await itens_da_pagina(fila)
            pendentes = [i for i in itens if i.processo not in concluidos]

            for lote in em_lotes(pendentes, cfg.abas):
                extraidos = await asyncio.gather(
                    *(extrair(abas[k], item, cfg) for k, item in enumerate(lote))
                )
                for resultado in extraidos:
                    checkpoint.gravar(resultado)
                    resultados.append(resultado)
                    concluidos.add(resultado.processo)
                    novos += 1

                decorrido = time.time() - inicio
                ritmo = decorrido / novos if novos else 0
                restantes = max(0, total - len(concluidos))
                print(
                    f"[pág {pagina}/{paginas}] {len(concluidos)} extraídos "
                    f"({ritmo:.1f}s/proc, ~{restantes * ritmo / 3600:.1f}h restantes)"
                )

                if cfg.limite and novos >= cfg.limite:
                    print(f"\nlimite de {cfg.limite} atingido")
                    await navegador.close()
                    return

            if not await proxima_pagina(fila, cfg):
                break
            pagina += 1

        await navegador.close()


def finalizar(resultados: list, inicio: float) -> None:
    destino = exportar(resultados)
    com_laudo = sum(1 for r in resultados if r.numero_sei)
    print(
        f"\n{len(resultados)} processos | {com_laudo} com laudo | "
        f"{(time.time() - inicio) / 60:.1f} min"
    )
    print(f"planilha: {destino}")


if __name__ == "__main__":
    asyncio.run(main())
