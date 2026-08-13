# Robô de Laudos — Isenção de Imposto de Renda (SEI-DF)

Automatiza a triagem que hoje é feita à mão: abrir cada processo de Isenção de IR no SEI, percorrer a árvore de documentos e procurar o laudo mais recente.

O robô varre a fila **Processos com Credencial na Unidade** (IPREV/DIPREV/COGEB/GEMF), separa os processos de Isenção de Imposto de Renda e, de cada um, extrai:

- o **último laudo** da árvore de documentos (o mais recente, de baixo para cima)
- a **unidade que subiu** esse laudo
- o **interessado** e a data de autuação

O resultado é uma planilha Excel em `saida/`.

---

## 1. Antes de começar

### 1.1 Instalar as dependências

Só na primeira vez, ou depois de trocar de computador:

```powershell
uv sync
uv run playwright install chromium
```

> **Por que `uv` e não `python`?** Neste computador não há Python no `PATH` — digitar `python` abre a loja da Microsoft. O `uv` cuida do interpretador e das bibliotecas sozinho. Sempre use `uv run`.

> **Sem `uv`?** As dependências também estão em `requirements.txt` (versões fixadas) para quem prefere `pip install -r requirements.txt`.

### 1.2 Preencher o `.env`

Na raiz do projeto existe o arquivo `.env`. Ele guarda suas credenciais e **nunca deve ser enviado para lugar nenhum** (já está protegido pelo `.gitignore`).

```ini
SEI_URL=https://sei.df.gov.br
SEI_USUARIO=seu.usuario
SEI_SENHA=sua_senha
SEI_Orgao=IPREV
SEI_SENHA_CREDENCIAL=sua_senha_de_credencial
```

| Campo | O que é |
|---|---|
| `SEI_USUARIO` / `SEI_SENHA` | O mesmo login e senha que você usa para entrar no SEI |
| `SEI_Orgao` | O órgão da tela de login. Aceita a sigla (`IPREV`) ou o código (`26`) |
| `SEI_SENHA_CREDENCIAL` | A senha que o SEI pede na janelinha ao abrir processo com credencial. Costuma ser igual à de login |
| `SEI_URL` | Pode deixar como está — o endereço de login já está fixo no código |

⚠️ **Erro de digitação aqui é a causa nº 1 de falha.** Se o usuário ou a senha estiverem errados, o robô para logo no início com a mensagem `Login recusado pelo SIP: Usuário ou Senha Inválida.`

---

## 2. Rodando

Abra o terminal **na pasta do projeto** e escolha um dos modos abaixo.

### 2.1 Pegar tudo (uso normal)

```powershell
uv run app.py
```

Varre a fila inteira, os ~6500 processos de Isenção. **Leva cerca de 5 horas.**

Ao terminar, a planilha aparece em `saida/laudos_<data>_<hora>.xlsx`.

Você pode fechar a janela ou o computador pode cair no meio — nada se perde, veja a seção 4.

### 2.2 Teste rápido (recomendado antes de uma rodada longa)

```powershell
$env:LIMITE="20"
uv run app.py
```

Extrai só 20 processos, em cerca de 1 minuto. Serve para confirmar que o login funciona e que os dados estão saindo certos antes de investir horas.

**Depois do teste, limpe a variável**, senão a próxima execução também vai parar em 20:

```powershell
Remove-Item env:LIMITE
```

### 2.3 Ver o navegador trabalhando

```powershell
$env:HEADLESS="false"
uv run app.py
```

Abre o Chrome na tela e você acompanha cada clique. Útil para entender o que ele faz ou para investigar um problema. É mais lento — não use na rodada completa.

Para voltar ao normal: `$env:HEADLESS="true"`.

---

## 3. Acompanhando o andamento

O terminal mostra o progresso a cada 4 processos:

```
[pág 58/138] 2779 extraídos (2.7s/proc, ~3.0h restantes)
```

**Para ver os dados sem esperar o fim**, abra um **segundo terminal** e rode:

```powershell
uv run parcial.py
```

Isso gera `saida/PARCIAL_<data>_<hora>.xlsx` com tudo que já foi extraído até aquele instante. Pode rodar quantas vezes quiser, não atrapalha a varredura.

> **Atenção ao nome do arquivo.** `PARCIAL_*.xlsx` é uma prévia incompleta. A planilha final é a `laudos_*.xlsx`, escrita só quando a varredura termina.

---

## 4. Se cair no meio

Não perde nada. Cada processo é gravado em `saida/checkpoint.jsonl` assim que é extraído.

Para continuar de onde parou, rode o mesmo comando de novo:

```powershell
uv run app.py
```

Ele relê a fila, pula o que já tem e continua. Vai aparecer no início:

```
retomando: 2801 processos já extraídos
```

**Para começar do zero**, apague o checkpoint antes:

```powershell
Remove-Item saida\checkpoint.jsonl
uv run app.py
```

---

## 5. Entendendo a planilha

| Coluna | Conteúdo |
|---|---|
| **Processo** | Número do protocolo |
| **Interessado** | Nome do segurado |
| **Autuação** | Data de abertura do processo |
| **Último laudo** | Nome do documento (ex.: `Laudo Médico`, `Laudo Técnico`) |
| **Nº SEI** | Número do documento no SEI. É crescente: quanto maior, mais recente |
| **Unidade que incluiu** | A área que subiu o laudo (ex.: `SEEC/SUBSAUDE/COPEM/DIPEM`) |
| **Docs** | Quantos documentos o processo tem no total |
| **Observação** | Vazia quando deu tudo certo |

A planilha já vem com filtro no cabeçalho e primeira linha congelada — dá para filtrar por unidade ou por tipo de laudo direto no Excel.

### 5.1 Por que existem células vazias

Isso é esperado e **não é erro do robô**. São três situações distintas:

**Último laudo / Nº SEI / Unidade vazios — cerca de 25% dos casos.**
O processo realmente não tem nenhum documento com "laudo" no nome. A coluna `Observação` mostra `sem laudo na árvore` e a coluna `Docs` prova que o robô leu a árvore (traz de 1 a 12+ documentos). Para a triagem, esse branco é justamente a informação útil: são os processos que ainda esperam laudo.

**Interessado vazio — cerca de 25% dos casos.**
Nesses processos o botão "Consultar Processo" não existe no SEI para o seu usuário: a credencial dá acesso ao processo, mas não à tela onde fica o nome. É limitação de permissão do SEI, sem contorno possível pelo robô.

**Observação preenchida.**
Só aparece quando houve um problema real com aquele processo. `sem laudo na árvore` é o caso normal; qualquer outra mensagem indica falha na leitura e vale investigar.

---

## 6. Ajustes finos

Todas opcionais, definidas no terminal antes de rodar (ou no `.env`):

| Variável | Padrão | Para que serve |
|---|---|---|
| `LIMITE` | vazio | Para depois de N processos. Use para testar |
| `ABAS` | `4` | Abas abertas em paralelo |
| `HEADLESS` | `false` | `true` roda sem abrir janela (mais rápido) |

**Sobre `ABAS`:** 4 é o valor testado e recomendado. Medição em 12 processos: 1 aba levou 58 s, 2 abas 45 s, 4 abas 23,6 s. Acima de 4 o SEI começa a engasgar e a perder dados — não aumente sem medir.

---

## 7. Problemas comuns

| O que aparece | O que fazer |
|---|---|
| `Login recusado pelo SIP: Usuário ou Senha Inválida` | Confira `SEI_USUARIO` e `SEI_SENHA` no `.env`. Cuidado com espaços sobrando |
| `SEI_Orgao=... não corresponde a nenhuma opção` | A mensagem lista os órgãos válidos. Copie um deles para o `.env` |
| `Preencha no .env: ...` | Falta preencher algum campo obrigatório |
| Parou em 20 processos sem motivo | Sobrou `LIMITE` de um teste anterior. Rode `Remove-Item env:LIMITE` |
| `paginação falhou` no terminal | Normal em execuções longas. Ele tenta 3 vezes e, se não conseguir, encerra **gravando a planilha** com tudo que já tem |
| A planilha veio com poucas linhas | Você abriu um `PARCIAL_*.xlsx`. A definitiva é `laudos_*.xlsx` |
| `python não foi encontrado` | Você digitou `python` em vez de `uv run` |

---

## 8. Cuidados

**Não rode dois `uv run app.py` ao mesmo tempo.** As duas execuções gravam no mesmo `checkpoint.jsonl` e atrapalham uma à outra. Para espiar o andamento, use `uv run parcial.py`.

**A planilha contém dados pessoais de saúde.** Nomes de segurados e laudos médicos. A pasta `saida/` já está fora do controle de versão; ao compartilhar o arquivo, trate-o com o cuidado que o assunto exige.

**O `.env` guarda sua senha do SEI.** Nunca copie esse arquivo para outro lugar nem o envie por e-mail ou chat.

---

## 9. Estrutura do projeto

```
app.py             varredura completa
parcial.py         gera planilha do que já foi extraído
sei/
  config.py        lê o .env
  login.py         login no SIP e senha de credencial
  fila.py          navega a fila e filtra Isenção de IR
  processo.py      lê a árvore, acha o laudo e o interessado
  checkpoint.py    salva o progresso
  export.py        monta a planilha
saida/             planilhas e checkpoint (não versionado)
```

Detalhes técnicos e as armadilhas do SEI estão no `CLAUDE.md`.
