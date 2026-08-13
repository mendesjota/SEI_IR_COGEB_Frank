# 🤖 Arquitetura do Robô: Raspagem de Isenção de IR no SEI

**Projeto:** Automação de triagem de processos de Isenção de Imposto de Renda.
**Diretório Local:** `SEI_IR_COGEB_Frank`
**Stack:** Python + Playwright (Modo Headless/Headed)
**Objetivo de Negócio (ROI):** Eliminar o tempo manual de abertura de processos e busca visual por laudos médicos, entregando os dados de forma instantânea e livre de falhas humanas.

---

## 1. O Desafio Técnico (Estrutura do SEI)
O SEI é um sistema construído com **Frames** (`iframes`). Isso significa que a página é dividida em janelas isoladas. O Playwright não consegue ler a árvore de documentos apenas olhando para a página principal; ele precisa "entrar" no iframe correto.
*   `ifrArvore`: O frame do lado esquerdo (onde fica a lista de documentos).
*   `ifrVisualizacao`: O frame do lado direito (onde o documento abre).

## 2. Lógica de Navegação e Execução

### Passo 1: Autenticação e Acesso à Fila
1. Acessar `https://sei.df.gov.br/sei`.
2. Inserir credenciais e logar.
3. Clicar no menu ou bloco de controle que contém os processos de **Isenção de Imposto de Renda**.

### Passo 2: O Loop de Processos
1. Mapear todos os links dos processos abertos na tela usando um seletor que pegue os números de protocolo.
2. Criar um laço `for` para clicar em cada processo um por um (ou abrir em novas abas para ganhar velocidade, dependendo da estabilidade do portal).

### Passo 3: A Busca pelo "Último Laudo" (Core Logic)
Assim que o processo abrir, o robô deve focar exclusivamente no `ifrArvore` (menu lateral esquerdo).

Como os processos do IPREV/Subsaúde podem ter dezenas de documentos, e queremos **apenas o último laudo anexado** (cronologicamente, o último da lista na árvore), a lógica de busca no Playwright será:

```python
# 1. Apontar para o iframe da árvore de documentos
arvore_frame = page.frame_locator("iframe[name='ifrArvore']")

# 2. Localizar o ÚLTIMO elemento que contenha a palavra "laudo" (ignorando maiúsculas/minúsculas)
ultimo_laudo = arvore_frame.locator("text=/laudo/i").last

# 3. Clicar no documento para ele abrir na tela da direita (ifrVisualizacao)
ultimo_laudo.click()