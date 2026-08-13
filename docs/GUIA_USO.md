# Guia Completo — Robô de Laudos de Isenção de Imposto de Renda (SEI-DF)

> Este guia explica **tudo** o que uma pessoa sem conhecimentos de programação
> precisa para baixar, configurar e rodar o robô, do início ao fim. Não se
> preocupe com termos técnicos: cada passo está explicado, com o que digitar e
> o que você deve ver acontecer na tela.

---

## Sumário

1. [O que este programa faz](#1-o-que-este-programa-faz)
2. [O que você precisa antes de começar](#2-o-que-você-precisa-antes-de-começar)
3. [Passo 1 — Baixar o projeto para o seu computador](#3-passo-1--baixar-o-projeto-para-o-seu-computador)
4. [Passo 2 — Instalar o uv (a ferramenta que roda o robô)](#4-passo-2--instalar-o-uv-a-ferramenta-que-roda-o-robô)
5. [Passo 3 — Abrir o "terminal" na pasta do projeto](#5-passo-3--abrir-o-terminal-na-pasta-do-projeto)
6. [Passo 4 — Criar o arquivo de configuração (.env) com suas credenciais](#6-passo-4--criar-o-arquivo-de-configuração-env-com-suas-credenciais)
7. [Passo 5 — Instalar as dependências (só na primeira vez)](#7-passo-5--instalar-as-dependências-só-na-primeira-vez)
8. [Passo 6 — Fazer um teste rápido](#8-passo-6--fazer-um-teste-rápido)
9. [Passo 7 — Rodar de verdade (a fila inteira)](#9-passo-7--rodar-de-verdade-a-fila-inteira)
10. [Passo 8 — Acompanhar e ver os resultados](#10-passo-8--acompanhar-e-ver-os-resultados)
11. [Entendendo a planilha](#11-entendendo-a-planilha)
12. [Se algo der errado (resolução de problemas)](#12-se-algo-der-errado-resolução-de-problemas)
13. [Perguntas frequentes](#13-perguntas-frequentes)
14. [Cuidados importantes com a privacidade](#14-cuidados-importantes-com-a-privacidade)

---

## 1. O que este programa faz

Imagine uma tarefa repetitiva que demora horas e exige abrir milhares de
processos um por um no SEI. Este programa faz essa tarefa sozinho.

Hoje, a triagem é feita à mão: uma pessoa abre cada processo de **Isenção de
Imposto de Renda**, procura na árvore de documentos o **laudo mais recente**
e anota a unidade que o incluiu. Com ~6.500 processos na fila, isso leva horas
e é cansativo.

O robô faz o seguinte, sem você precisar tocar em nada:

1. Entra no SEI com o **seu** usuário e senha.
2. Abre a fila **"Processos com Credencial de Segurança"**.
3. Separa apenas os processos de **Isenção de Imposto de Renda**.
4. Em cada um, procura o **último laudo** da árvore de documentos.
5. Anota a **unidade** que incluiu o laudo, o **interessado** e a **data de autuação**.
6. No final, gera uma **planilha Excel** com tudo organizado.

O resultado é uma planilha em Excel que você pode filtrar, ordenar e usar
direto na triagem.

---

## 2. O que você precisa antes de começar

- Um **computador com Windows** (é o sistema usado neste guia).
- **Acesso à internet**.
- Seu **login do SEI** (usuário e senha) e a **senha de credencial**
  (a senha que o SEI pede na janelinha quando você abre um processo com
  credencial de segurança).
- **Não precisa de nenhum conhecimento de programação.** O guia mostra tudo.

---

## 3. Passo 1 — Baixar o projeto para o seu computador

Você tem duas formas. **Para quem não usa programação, recomendamos a forma
com o ZIP** (mais simples).

### Opção A — Baixar como ZIP (mais fácil)

1. Acesse a página do projeto no GitHub.
2. Clique no botão verde **"Code"** (no lado direito da página).
3. No menu que abrir, clique em **"Download ZIP"**.
4. O navegador baixa um arquivo compactado (terminado em `.zip`).
5. Encontre o arquivo baixado, **clique com o botão direito** e escolha
   **"Extrair tudo..."**.
6. Escolha uma pasta de destino. **Evite pastas com espaços no nome do caminho.**
   O Windows costuma criar uma pasta com o nome do projeto — pode usar ela mesmo.
7. Anote onde o projeto foi extraído: você vai precisar achar essa pasta nos
   próximos passos. Ela contém um arquivo chamado `app.py`.

### Opção B — Clonar com o Git (para quem já usa Git)

No terminal, dentro da pasta onde quer o projeto:

```
git clone https://github.com/mendesjota/SEI_IR_COGEB_Frank.git
```

---

## 4. Passo 2 — Instalar o uv (a ferramenta que roda o robô)

O projeto usa uma ferramenta chamada **uv**, que cuida sozinha do Python e das
bibliotecas necessárias. Você precisa instalá-la **uma única vez** por
computador.

1. Abra o **PowerShell** (Menu Iniciar → digite `powershell` → Enter).
2. Cole o comando abaixo e pressione Enter:

```
winget install --id=astral-sh.uv -e
```

3. O Windows baixa e instala o uv. Quando terminar, **feche e abra o
   PowerShell de novo** (para o Windows reconhecer o programa novo).
4. Para conferir se deu certo, digite e pressione Enter:

```
uv --version
```

Você deve ver algo como `uv 0.x.x`. Se aparecer essa mensagem, parabéns: a
ferramenta principal está instalada.

> **Se o `winget` não funcionar** (aparecer "não reconhecido"), use o
> instalador alternativo, colando isto no PowerShell:
> `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
> Depois, feche e reabra o PowerShell e teste com `uv --version`.

---

## 5. Passo 3 — Abrir o "terminal" na pasta do projeto

O **terminal** (ou PowerShell) é a janela preta onde você digita comandos. O
segredo é abri-lo **dentro da pasta do projeto**, senão o computador não
encontra o programa.

1. No Explorador de Arquivos, **navegue até a pasta do projeto** (a que você
   extraiu no Passo 1, onde está o arquivo `app.py`).
2. Clique na **barra de endereço** (onde aparece o caminho, tipo
   `C:\Usuários\...`), **apague o que estiver lá**, digite `powershell` e
   pressione Enter.
3. Vai abrir uma janela preta (ou azul) já dentro da pasta certa. Para ter
   certeza, digite e pressione Enter:

```
dir
```

Você deve ver a lista de arquivos do projeto, incluindo o `app.py`. Se vir,
está no lugar certo.

> **Dica:** a partir de agora, todas as vezes que este guia disser "no
> terminal", é nesta janela que você digita o comando.

---

## 6. Passo 4 — Criar o arquivo de configuração (.env) com suas credenciais

O robô precisa saber **quem é você** para entrar no SEI. Essas informações
ficam em um arquivo de texto chamado `.env`.

O projeto já vem com um modelo chamado **`.env.example`**. Vamos copiá-lo e
chamá-lo de `.env` — é nele que você vai escrever suas informações.

1. No terminal (na pasta do projeto), cole e pressione Enter:

```
Copy-Item .env.example .env
```

2. Agora abra o arquivo `.env` no Bloco de Notas, com este comando:

```
notepad .env
```

3. O Bloco de Notas abre com o conteúdo do arquivo. Preencha os campos
   conforme a tabela abaixo. **Não use acentos nem deixe espaços extras**
   (ex.: `SEI_USUARIO=jose.silva`, sem espaço depois do `=`).

| Campo | O que colocar |
|---|---|
| `SEI_URL` | Deixe como está (`https://sei.df.gov.br`). |
| `SEI_USUARIO` | O seu usuário de acesso ao SEI. |
| `SEI_SENHA` | A sua senha de acesso ao SEI. |
| `SEI_Orgao` | O órgão da tela de login. Pode ser a sigla (`IPREV`) ou o código (`26`). |
| `SEI_SENHA_CREDENCIAL` | A senha que o SEI pede na janelinha ao abrir processo com credencial. Costuma ser igual à de login. |
| `HEADLESS` | `false` para você ver o navegador trabalhando; `true` para rodar escondido (mais rápido). |
| `ABAS` | Quantos processos abertos ao mesmo tempo. **Deixe `4`** — é o valor testado e recomendado. |
| `LIMITE` | Deixe **vazio** para varrer a fila inteira. Só usa números para testes (ver Passo 6). |

4. **Salve o arquivo** (Bloco de Notas → menu Arquivo → Salvar) e feche.

> ⚠️ **O arquivo `.env` contém suas senhas.** Nunca o envie para ninguém, nem
> por e-mail, nem por chat, e nunca o cole em lugar público. Na próxima seção
> entendemos o porquê.

> 💡 **Cuidado com o Bloco de Notas:** confira se o arquivo salvo continua
> chamado `.env` (e não `.env.txt`). Se o Windows esconder a extensão, apenas
> siga os passos; o robô avisa se não encontrar o arquivo.

---

## 7. Passo 5 — Instalar as dependências (só na primeira vez)

O robô precisa de algumas bibliotecas auxiliares e do navegador Chromium.
Instale agora, **antes da primeira execução**.

No terminal (na pasta do projeto), um comando por vez:

```
uv sync
```

Esse comando baixa e prepara tudo o que o projeto precisa. Pode demorar um
pouco na primeira vez. Quando terminar, digite:

```
uv run playwright install chromium
```

Esse segundo comando baixa o navegador que o robô usa. Também demora um pouco
na primeira vez.

> **Repare no padrão:** os comandos que rodam o projeto sempre começam com
> `uv run`. É assim que você chama o programa aqui — nunca digite só `python`.

---

## 8. Passo 6 — Fazer um teste rápido

Antes de investir horas, é prudente testar com **poucos processos**. Se algo
estiver errado, você descobre em um minuto, não em cinco horas.

1. No terminal, cole e pressione Enter:

```
$env:LIMITE="12"
```

Isso diz ao robô: "pare depois de 12 processos". (É só um teste.)

2. Agora rode o robô:

```
uv run app.py
```

3. O que deve acontecer:
   - Uma janela do **navegador Chrome abre sozinha** (porque `HEADLESS=false`).
   - O robô entra no SEI, passa a senha de credencial e começa a abrir
     processos.
   - No terminal você vê mensagens de progresso, ex.:
     `[pág 1/1] 12 extraídos (2.7s/proc, ~0.0h restantes)`.
   - Ao final, o robô fecha e mostra onde salvou a planilha.

4. **Importante:** depois do teste, limpe a variável `LIMITE`, senão a próxima
   execução também vai parar em 12 processos:

```
Remove-Item env:LIMITE
```

5. Confira a planilha gerada (veja o Passo 10 para achar o arquivo). Se os
   dados estão aparecendo e fazendo sentido, está tudo pronto para a rodada
   completa.

> **Se der erro de login** (mensagem como "Login recusado pelo SIP"), quase
> sempre é credencial errada no `.env`. Veja a seção 12.

---

## 9. Passo 7 — Rodar de verdade (a fila inteira)

Com o teste aprovado, hora de varrer a fila inteira.

1. No terminal, rode:

```
uv run app.py
```

2. O robô mostra no começo quantos processos há na fila, por exemplo:

```
fila com 6850 processos (~138 páginas), 4 abas
```

3. Ele trabalha sozinho. No terminal, a cada lote, aparece uma linha de
   progresso como esta:

```
[pág 58/138] 2779 extraídos (2.7s/proc, ~3.0h restantes)
```

   Ela diz: página 58 de 138, já extraiu 2.779 processos, e quanto tempo (por
   estimativa) ainda falta.

> ⏱️ **Quanto demora?** A fila inteira leva **em torno de 1,5 a 5 horas**,
> dependendo do computador e da internet. É normal.

> 🔌 **Pode fechar o terminal no meio?** Sim! O robô grava o progresso a cada
> processo em um arquivo chamado `checkpoint.jsonl`. Se você parar (fechar a
> janela, reiniciar o PC), basta **rodar `uv run app.py` de novo** que ele
> continua de onde parou, sem repetir o que já foi feito.

> 🖥️ **Quer ver o navegador trabalhando?** Já está no padrão
> (`HEADLESS=false`). Para rodar escondido (mais rápido, sem janela), edite o
> `.env` e troque `HEADLESS=false` por `HEADLESS=true`.

---

## 10. Passo 8 — Acompanhar e ver os resultados

### Ver a planilha parcial (sem esperar o fim)

Você não precisa esperar a varredura inteira para ver dados. Abra um
**segundo terminal** (pode ser na mesma pasta) e rode:

```
uv run parcial.py
```

Ele gera uma planilha **preliminar** com tudo o que já foi extraído até aquele
instante. Pode rodar quantas vezes quiser — não atrapalha a varredura em
andamento.

### Achar a planilha final

Todas as planilhas ficam na pasta **`saida/`**, dentro do projeto:

```
saida/
  laudos_2026-08-13_1530.xlsx     ← a planilha final (varredura completa)
  PARCIAL_2026-08-13_1530.xlsx    ← uma prévia parcial (se você rodou o parcial.py)
```

- O nome traz a data e a hora em que foi gerada.
- **A definitiva é a que começa com `laudos_`** (sem o `PARCIAL_`).
- Abra o `.xlsx` no Excel normalmente, com dois cliques.

---

## 11. Entendendo a planilha

A planilha tem uma linha por processo e as colunas abaixo:

| Coluna | O que significa |
|---|---|
| **Processo** | O número do protocolo no SEI. |
| **Interessado** | O nome da pessoa dona do processo. |
| **Autuação** | A data de abertura do processo. |
| **Último laudo** | O nome do laudo mais recente (ex.: `Laudo Médico`). |
| **Nº SEI** | O número do documento no SEI. Quanto maior, mais recente. |
| **Unidade que incluiu** | A área que subiu o laudo (ex.: `SEEC/SUBSAUDE/COPEM/DIPEM`). |
| **Docs** | Quantos documentos o processo tem ao todo. |
| **Observação** | Anotações do robô. Vazia = deu tudo certo. |

A planilha já vem com **filtro** no cabeçalho e **primeira linha congelada**:
use as setinhas nas colunas para filtrar por unidade, por tipo de laudo etc.,
como em qualquer planilha.

### Por que existem células vazias? (isso é normal)

- **Último laudo / Nº SEI / Unidade vazios (cerca de 25% dos casos):**
  o processo realmente **não tem laudo** na árvore. A coluna Observação mostra
  `sem laudo na árvore` e a coluna Docs prova que o robô leu a árvore. Para a
  triagem, esse branco é justamente a informação útil: são os processos que
  ainda esperam laudo.
- **Interessado vazio (cerca de 25% dos casos):**
  nesses processos o botão "Consultar Processo" não existe para o seu usuário
  no SEI. É limitação de permissão, sem contorno pelo robô.
- **Observação preenchida com outra coisa:**
  indica um problema real com aquele processo e vale investigar.

---

## 12. Se algo der errado (resolução de problemas)

| O que apareceu | O que fazer |
|---|---|
| `Login recusado pelo SIP: Usuário ou Senha Inválida` | Confira `SEI_USUARIO` e `SEI_SENHA` no `.env`. Cuidado com espaços extras ou caracteres errados. |
| `SEI_Orgao=... não corresponde a nenhuma opção` | A mensagem lista os órgãos válidos. Copie um deles para o `.env`. |
| `Preencha no .env: ...` | Falta preencher algum campo obrigatório. Abra o `.env` e complete. |
| Parou em 12 (ou outro número) processos sem motivo | Sobrou o `LIMITE` de um teste. Rode `Remove-Item env:LIMITE` e rode de novo. |
| `paginação falhou` no terminal | É normal em execuções longas. O robô tenta 3 vezes e, se não conseguir, **encerra gravando a planilha** com tudo que já tem. Basta rodar de novo para continuar. |
| A planilha veio com poucas linhas | Você abriu um `PARCIAL_*.xlsx` (prévia). A definitiva é a `laudos_*.xlsx`, gerada quando a varredura termina. |
| `python não foi encontrado` | Você digitou `python` em vez de `uv run`. Use sempre `uv run`. |
| `uv não é reconhecido` | O uv não foi instalado ou o terminal não foi reaberto. Volte ao Passo 2. |
| A janela do navegador não abre | `HEADLESS=true` no `.env` roda escondido. É normal — o robô continua trabalhando. |

---

## 13. Perguntas frequentes

**Posso fechar o computador no meio da varredura?**
Pode. O progresso fica salvo. Quando ligar de novo, rode `uv run app.py` e ele
continua de onde parou.

**Quero recomeçar do zero (apagar tudo que já foi extraído).**
Apague o arquivo de progresso e rode de novo:

```
Remove-Item saida\checkpoint.jsonl
uv run app.py
```

> Cuidado: só apague o checkpoint se quiser mesmo repetir a extração toda.

**Posso rodar duas varreduras ao mesmo tempo?**
**Não.** As duas gravariam no mesmo arquivo de progresso e atrapalhariam uma à
outra. Para espiar o andamento, use `uv run parcial.py` em outro terminal.

**Preciso do Python instalado?**
Não. O `uv` cuida de tudo sozinho.

**Mudou a senha do SEI?**
Atualize o `.env` e rode de novo. Não precisa reinstalar nada.

**Quero que ele rode mais rápido.**
O padrão (`ABAS=4`) já é o valor recomendado. Acima disso o SEI começa a
engasgar e a perder dados — não aumente sem medir.

---

## 14. Cuidados importantes com a privacidade

Este projeto lida com **dados pessoais de saúde**:

- A **planilha** gerada contém nome de segurados e o tipo de laudo (Isenção de
  IR é concedida por doença grave). Trate esses arquivos como segredos: não os
  envie por e-mail, não os suba em nuvens públicas, não os deixe em pastas
  compartilhadas. A pasta `saida/` já está protegida para não ser publicada no
  Git, mas isso não substitui o bom senso ao compartilhar os arquivos.
- O arquivo **`.env`** contém suas senhas do SEI. Nunca o copie, envie ou
  publique. Ele também já está protegido no Git.
- **O que pode ser publicado** (código, documentação, este guia) **não contém**
  nenhum dado pessoal de terceiros nem credenciais — foi projetado para que um
  vazamento acidental não exponha nada.

---

*Documentação didática do projeto SEI_IR_COGEB_Frank — para uso com `uv run app.py`.*