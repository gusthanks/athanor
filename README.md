# Athanor

**Transform scattered projects into living operating systems.**

Athanor is an open-source, workspace-first system for helping people and AI
agents understand, structure, preserve, operate, and evolve real projects.
It can start from an empty folder, a mature codebase, a creative archive, or a
mixed business workspace.

The package is one installable plugin with focused internal skills:

- `athanor` — entry point and router
- `athanor-help` — contextual guidance
- `athanor-init` — project operating-system bootstrap
- `athanor-audit` — maturity and gap assessment
- `athanor-organize` — plan-first, reversible organization
- `athanor-chronicle` — Git, GitHub, backup, and preservation
- `athanor-team` — agents, authority, and handoffs
- `athanor-integrate` — APIs, MCP, connectors, and automation
- `athanor-maintain` — memory, drift, and ongoing governance

## Princípio central

O Athanor não reorganiza, publica, conecta serviços, envia dados ou cria uma
equipe autônoma às cegas. Ele primeiro torna o estado atual visível, propõe uma
transformação verificável, separa ações reversíveis das ações de alto impacto e
só então executa o que foi autorizado.

## Começar

Leia o [Handbook](docs/HANDBOOK.md) para entender o sistema sem depender de uma
IA. Veja [Instalação](docs/INSTALLATION.md) para adicionar o plugin ao Codex a
partir desta pasta ou de um clone do GitHub.

No Windows:

```powershell
.\install.ps1 -Target codex
.\install.ps1 -Target claude
.\install.ps1 -Target antigravity
```

Use `-Target all` para instalar em todos os runtimes suportados. Claude e
Antigravity recebem links para esta única fonte, evitando cópias desatualizadas.

Diagnostique a fonte e todas as instalações sem alterar o workspace:

```powershell
.\install.ps1 -Target all -Action doctor
```

Depois, invoque:

```text
$athanor
```

Ou descreva o resultado desejado:

```text
Use $athanor para diagnosticar este projeto e me dizer o que falta.
```

## Requisitos

- Python 3.10 ou superior para os utilitários determinísticos.
- Git é opcional e só é necessário para o módulo Chronicle.
- Nenhum MCP, API ou serviço pago é obrigatório.
- Datas e nomes datados usam `YYYY-MM-DD`.
- Codex, Claude Code e Google Antigravity são suportados pelos instaladores.

## O que existe além do `SKILL.md`

Uma skill pode começar como um `SKILL.md`, mas o Athanor também inclui
referências carregadas sob demanda, templates, scripts determinísticos, testes,
metadados de interface e um manifesto de plugin. Leia
[Anatomia](docs/ANATOMY.md) para entender o que cada camada faz.

## Segurança por arquitetura

- auditoria não lê o conteúdo de arquivos classificados como segredo;
- organização é plano-primeiro e dry-run por padrão;
- arquivos existentes não são sobrescritos no bootstrap;
- conexões são recomendadas conforme a necessidade, não embutidas à força;
- MCPs, APIs e conectores exigidos por um objetivo são explicados com
  pré-requisitos, custo, permissões, testes e fallback;
- publicação, gasto, credenciais, dados pessoais e mutações externas mantêm
  aprovação humana.

## Estado

Versão `0.3.0`: diagnóstico de instalação, atualização segura dos runtimes,
configuração independente de colaboração e garantia, checkpoints, destilação
de conhecimento e dependências leves entre tarefas. Consulte o
[changelog](CHANGELOG.md) e a [matriz de
compatibilidade](docs/COMPATIBILITY.md).

## Licença

MIT. Veja [LICENSE](LICENSE).
