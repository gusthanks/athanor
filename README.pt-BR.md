# Athanor

[English](README.md) | **Português (Brasil)**

[![CI](https://github.com/gusthanks/athanor/actions/workflows/ci.yml/badge.svg)](https://github.com/gusthanks/athanor/actions/workflows/ci.yml)
[![Licença: MIT](https://img.shields.io/badge/licen%C3%A7a-MIT-blue.svg)](LICENSE)

**Skills de agente para Claude Code, Codex e Google Antigravity que auditam
qualquer pasta de projeto e dão a ela um contexto durável que seus agentes
realmente usam: resumo do projeto, tarefas, decisões, ferramentas e riscos,
além de reorganização segura de arquivos. Nada é movido, publicado ou conectado
a um serviço antes da sua aprovação.**

O problema: toda sessão nova de agente começa do zero. Ele pergunta de novo o
que é o projeto, chuta onde está a fonte de verdade e "arruma" pastas que não
entende. O Athanor é para quem toca projetos reais com agentes de IA (código,
acervos criativos, workspaces de pequenos negócios) e quer que esses agentes
trabalhem a partir de contexto verificado, em arquivos simples, e não de
memória e palpite.

## Começo rápido (30 segundos)

**Claude Code** (plugin nativo, sem clone e sem configurar Python):

```text
/plugin marketplace add gusthanks/athanor
/plugin install athanor@athanor-community
```

Abra qualquer projeto e rode:

```text
/athanor:athanor diagnostique este projeto e me diga o que falta
```

**Codex ou Google Antigravity** (a partir de um clone, Python 3.10+):

```bash
git clone https://github.com/gusthanks/athanor.git
cd athanor
./install.sh codex          # ou: ./install.sh antigravity, ./install.sh all
```

Depois invoque `$athanor` no Codex ou peça ao agente do Antigravity para usar
`athanor`. No Windows, use `.\install.ps1 -Target codex`. Veja
[Instalação](docs/INSTALLATION.md) (em inglês) para todos os runtimes,
simulação, diagnóstico, atualização e desinstalação.

Diagnostique a fonte e todas as instalações sem alterar o workspace:

```bash
./install.sh all doctor
```

## O que você recebe

A primeira passagem é somente leitura. O Athanor inventaria a pasta (sem ler
arquivos de segredo), relata fatos verificados, lacunas e riscos imediatos e
propõe um próximo passo. Quando você aprova o bootstrap, ele adiciona um
conjunto pequeno de arquivos Markdown e nunca sobrescreve os existentes:

```text
seu-projeto/
├── AGENTS.md                    # ponto de entrada para qualquer agente (mesclado, não substituído)
├── CLAUDE.md                    # aponta o Claude Code para as mesmas fontes
└── athanor/
    ├── PROJECT.md               # identidade, fontes de verdade, invariantes
    ├── DECISIONS.md             # decisões humanas com data e procedência
    ├── TASKS.md                 # trabalho aberto, dependências, handoff atual
    ├── TOOLS.md                 # capacidades verificadas das ferramentas
    ├── INTEGRATIONS.md          # conexões externas e estado de aprovação
    ├── RISKS.md
    ├── ROSTER.md                # agentes, autoridade e handoffs
    ├── ORGANIZATION-REVIEW.md   # arquivos sobre os quais o Athanor ficou em dúvida
    └── config.json              # estilo de colaboração e nível de garantia
```

Qualquer agente ou pessoa consegue ler esses arquivos. Eles não dependem do
Athanor.

## Módulos

Um plugin, nove skills focadas:

| Skill | O que faz |
| --- | --- |
| `athanor` | Entrada e roteador. Leva o pedido ao módulo certo. |
| `athanor-help` | Explica um conceito no seu nível e sugere uma única próxima ação segura. |
| `athanor-init` | Faz o bootstrap dos arquivos acima sem sobrescrever nada. |
| `athanor-audit` | Avaliação de maturidade e lacunas, só com metadados. |
| `athanor-organize` | Reorganização plano-primeiro: simulação, aprovação por linha, backup, registro de hash, sem deleção. |
| `athanor-chronicle` | Git, GitHub, LFS, backup e preservação. |
| `athanor-team` | Desenha agentes por responsabilidade e risco, com handoffs explícitos. |
| `athanor-integrate` | Compara processo manual, conector, no-code, API e MCP antes de conectar qualquer coisa. |
| `athanor-maintain` | Destilação de memória, verificação de desvio e checkpoints append-only. |

No Claude Code, as skills do plugin têm namespace: `/athanor:athanor-audit`,
`/athanor:athanor-organize` e assim por diante. O Claude também pode escolher
um módulo sozinho quando o pedido combina com a descrição dele.

## Princípio central

O Athanor não reorganiza, publica, conecta serviços, envia dados ou cria uma
equipe autônoma às cegas. Ele primeiro torna o estado atual visível, propõe uma
transformação verificável, separa ações reversíveis das ações de alto impacto e
só então executa o que foi autorizado.

## Segurança por arquitetura

- auditoria não lê o conteúdo de arquivos classificados como segredo;
- organização é plano-primeiro e dry-run por padrão, e o aplicador recusa
  sobrescrita, caminhos fora da raiz e deleção;
- arquivos existentes não são sobrescritos no bootstrap;
- conexões são recomendadas conforme a necessidade, não embutidas à força;
- MCPs, APIs e conectores exigidos por um objetivo são explicados com
  pré-requisitos, custo, permissões, testes e fallback;
- publicação, gasto, credenciais, dados pessoais e mutações externas mantêm
  aprovação humana.

## Por que não só um CLAUDE.md?

Um `AGENTS.md` ou `CLAUDE.md` escrito à mão é um bom começo, e o Athanor
preserva o seu. O que ele acrescenta é a disciplina em volta: auditoria antes
de qualquer escrita, arquivos separados para decisões, tarefas e ferramentas
(para não virarem um prompt longo e desatualizado), um jeito determinístico e
reversível de mover arquivos e verificações que pegam desvios depois. Veja
[Diferenciação](docs/DIFFERENTIATION.md) (em inglês).

## Requisitos

- Claude Code, Codex ou Google Antigravity.
- Python 3.10 ou superior para os utilitários determinísticos.
- Git é opcional e só é necessário para o módulo Chronicle e para atualizações.
- Nenhum MCP, API ou serviço pago é obrigatório.
- Datas e nomes datados usam `YYYY-MM-DD`.

## Saiba mais

- [Handbook](docs/HANDBOOK.pt-BR.md): entenda o sistema sem depender de uma IA.
- [Anatomia](docs/ANATOMY.md) (em inglês): o que existe além do `SKILL.md`
  (referências carregadas sob demanda, templates, scripts determinísticos,
  testes, metadados de interface e manifestos de plugin).
- [Arquitetura](docs/ARCHITECTURE.md), [Cenários](docs/SCENARIOS.md),
  [Compatibilidade](docs/COMPATIBILITY.md) (em inglês).

O nome vem do forno do alquimista, que mantém um fogo lento e constante. O
vocabulário alquímico (Scribe, Alchemist, Adept, Nigredo, Rubedo) é só uma
camada de experiência; arquivos e relatórios usam nomes claros.

## Estado

Versão `0.3.0`: diagnóstico de instalação, atualização segura dos runtimes,
configuração independente de colaboração e garantia, checkpoints, destilação
de conhecimento, dependências leves entre tarefas e plugin nativo para Claude
Code. Consulte o [changelog](CHANGELOG.md).

## Licença

MIT, © 2026 Gustavo Costa (gusthx). Veja [LICENSE](LICENSE).
