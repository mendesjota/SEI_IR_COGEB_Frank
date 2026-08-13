# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## O que este projeto faz

Robô Playwright que varre a fila **Processos com Credencial de Segurança** do SEI-DF (unidade IPREV/DIPREV/COGEB/GEMF), filtra os processos de **Isenção de Imposto de Renda** e extrai, de cada um, o **último laudo da árvore de documentos** e a **unidade que o incluiu**. Saída: `saida/laudos_AAAA-MM-DD_HHMM.xlsx`.

Escala real: ~6850 processos na fila, dos quais ~6492 são de Isenção. Varredura completa leva cerca de 1,5 h com `ABAS=4`.

## Comandos

Não há Python no `PATH` (só o alias da Store, que falha). Use **uv**:

```powershell
uv run app.py                    # varredura completa
uv run playwright install chromium
```

Testar sem varrer tudo: `$env:LIMITE="12"; $env:HEADLESS="false"; uv run app.py`

Não há testes automatizados — a validação é comparar a planilha com o SEI aberto ao lado.

## Variáveis de ambiente

`.env` (template em [.env.example](.env.example)), lido via `python-dotenv` em [sei/config.py](sei/config.py):

| Variável | Uso |
|---|---|
| `SEI_USUARIO` / `SEI_SENHA` | Login no SIP |
| `SEI_Orgao` | Órgão do combo. Aceita sigla (`IPREV`) ou o value (`26`) — `selecionar_orgao` tenta as duas |
| `SEI_SENHA_CREDENCIAL` | Senha do modal de credencial de segurança |
| `SEI_URL` | Ignorada, a menos que contenha `login.php` (ver abaixo) |
| `HEADLESS`, `ABAS`, `LIMITE` | Controlam a execução |

## Fatos do SEI que custaram caro descobrir

Estes pontos não são dedutíveis do código e quebram qualquer reescrita ingênua:

1. **O login não é no SEI, é no SIP.** URL fixa em `URL_LOGIN_SIP` ([sei/config.py](sei/config.py)). `SEI_URL` só é usada se contiver `login.php`.

2. **`infra_hash` vale só para a sessão que o gerou.** Salvar URLs de processos e reusá-las depois não apenas falha — o SIP responde "Hash inválido" e **derruba a sessão inteira**. Por isso [sei/fila.py](sei/fila.py) trabalha página a página: lê os 50 links da página atual e abre esses processos imediatamente, na mesma sessão. Nunca colete todas as URLs antes.

3. **O modal `iframe[name="modal-frame"]` é a senha de credencial**, e reaparece **em todo processo aberto** — às vezes duas vezes seguidas. `resolver_modal_credencial` é idempotente de propósito: chame após todo `goto` e toda paginação. Esquecer isso faz a árvore nunca carregar, com timeout enganoso.

   Ele é também **o gargalo do robô**: medido, 3,98 s dos 4,12 s de cada processo (97%). O desperdício não era o modal em si, e sim a segunda volta do laço esperando o timeout cheio por um modal que não vinha. Só a primeira espera usa o timeout cheio; as seguintes usam 700 ms, e o fim é detectado por `wait_for(state="hidden")` em vez de um sleep fixo. Isso levou o processo de 4,12 s para 1,89 s. **Não aumente esses valores sem medir** — cada 100 ms aqui equivale a ~11 min na fila inteira.

4. **`all_inner_texts()` não espera nada.** Sem um `wait_for(state="attached")` antes, devolve `[]` em silêncio e o processo entra na planilha como "sem laudo". Foi a causa de um falso negativo durante o desenvolvimento.

5. **A árvore alterna documento e unidade.** O link imediatamente após cada documento traz a sigla da área que o incluiu — é daí que sai a "área que adicionou", sem precisar abrir nada:
   ```
   'Laudo Médico (200000002)'
   'IPREV/DIPREV/COCAT/GEAS'   ← unidade
   ```
   **O separador nem sempre é `/`.** Existem siglas com underscore, como `SEEC_SUBSAUDE/COPEM/DIPEM`. Um `SIGLA_UNIDADE` que exigisse apenas a barra deixou 733 laudos (15%) com a coluna Unidade vazia na primeira varredura completa — e o pior é que a falha é silenciosa: o laudo sai certo, só a unidade some. Ao mexer nesse regex, valide contra as duas formas.

6. **Nem todo documento usa parênteses**: `Requerimento (200000000)` mas `Despacho 200000001`. A regex `DOCUMENTO` cobre os dois; os 5+ dígitos exigidos descartam o nó raiz do processo.

7. **`ifrVisualizacao` é aninhado.** `page.frame_locator("iframe[name='ifrVisualizacao']")` no topo dá timeout; use `page.frame(name="ifrVisualizacao")`.

8. **O interessado não existe** nem na fila nem em nenhum dos 5 frames do processo (verificado: 0 ocorrências de "Interessado"). Ele vive na tela **Consultar Processo**, em `#selInteressadosProcedimento` (um `<option>` por interessado), alcançada pelo botão `a:has(img[alt="Consultar Processo"])` dentro de `ifrConteudoVisualizacao`.

   Três armadilhas, todas já pagas:
   - **Use o `href` do botão, não uma URL montada.** Ele traz um `infra_hash` válido gerado pelo servidor; inventar a URL derruba a sessão (ver item 2).
   - **A base do `urljoin` é `aba.url`, não a url do frame.** O frame pode estar em `about:blank`, e o `urljoin` produziria uma URL inválida que leva o `goto` para lugar nenhum — falha que se disfarça de timeout do seletor.
   - **`extrair_interessado` navega a aba para fora** da tela do processo. Chame só depois de a árvore já ter sido lida e convertida em texto.

   **Cobertura: 75%** (medida em amostra de 36 processos espalhados por toda a fila). No restante, o botão não existe no HTML — o acesso por credencial não dá direito à tela de consulta. Não é bug e não é recuperável; a coluna fica vazia. Há correlação observada: processos **com** laudo tendem a **não** expor o interessado, então amostras da página 1 (ricas em laudo) subestimam muito a cobertura real.

9. **O nó raiz da árvore não lista protocolos com datas** — mostra "Processo aberto com os usuários". A data de inclusão do laudo só sai do "Consultar Andamento" + "Ver histórico completo", o que quase triplica o tempo. Por decisão do usuário, a planilha usa a **data de autuação** do processo, que vem de graça na fila.

10. **Paralelismo exige retry.** Sem `TENTATIVAS` em [sei/processo.py](sei/processo.py), 4 abas perdiam laudos silenciosamente — o timeout virava "sem laudo" na planilha, um falso negativo indistinguível de um processo legítimo sem laudo. Com retry, 4 abas entregam ~0,9 s/processo (a fila inteira em ~1,6 h).

    Cuidado ao medir: repetir o teste sobre os mesmos 12 processos dá números otimistas demais. Meça sempre com o checkpoint preenchido, sobre processos ainda não visitados.

## Estrutura

```
app.py               orquestra: login -> fila -> lotes de ABAS processos -> xlsx
sei/config.py        Config lida do .env
sei/login.py         login no SIP + resolver_modal_credencial
sei/fila.py          paginação da fila, filtro de Isenção, ItemFila
sei/processo.py      árvore -> documentos -> último laudo (+ retry)
sei/checkpoint.py    JSON Lines, permite retomar
sei/export.py        planilha
```

O código do Playwright é **async** (`playwright.async_api`): a API síncrona não permite abas concorrentes.

`saida/checkpoint.jsonl` guarda cada processo assim que é extraído. Ao reiniciar, o que já está lá é pulado — apague o arquivo para forçar varredura do zero.

Para corrigir um defeito de extração sem refazer tudo: remova do `checkpoint.jsonl` apenas as linhas afetadas (fazendo backup antes) e rode `uv run app.py`. A fila é repercorrida, mas só os processos ausentes são reabertos. Foi assim que os 735 registros sem unidade foram consertados sem repetir as ~2 h dos outros 5747.

`uv run parcial.py` gera a planilha do que já está no checkpoint, sem tocar no navegador — pode rodar com a varredura em andamento.

## Convenções

- Documentação e comentários em português.
- `saida/` está no `.gitignore`: a planilha contém dados pessoais de saúde.
- [raspagem_sei.py](raspagem_sei.py) é o codegen original, mantido só como referência histórica. Contém o login em texto plano (a "senha" ali são caracteres de máscara U+25CF, não a senha real).
