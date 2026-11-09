# Athanor Handbook

## Sumário

1. [O que é](#o-que-é)
2. [Instalação](#instalação)
3. [Como começar](#como-começar)
4. [Colaboração e garantia](#colaboração-e-garantia)
5. [As fases do trabalho](#as-fases-do-trabalho)
6. [O que o Athanor diagnostica](#o-que-o-athanor-diagnostica)
7. [Organização segura](#organização-segura)
8. [Git, GitHub e preservação](#git-github-e-preservação)
9. [Agentes e memória](#agentes-e-memória)
10. [Integrações](#integrações)
11. [Aprovações e segurança](#aprovações-e-segurança)
12. [Datas](#datas)
13. [Ajuda](#ajuda)
14. [Saúde, atualização e continuidade](#saúde-atualização-e-continuidade)

## O que é

Athanor é um sistema de orientação e governança para projetos. Ele ajuda uma
pessoa e seus agentes de IA a responder:

- o que este projeto é;
- onde está cada fonte de verdade;
- o que já existe e o que ainda falta;
- quem decide e quem executa;
- quais agentes são realmente necessários;
- quais ferramentas e integrações valem a pena;
- o que deve ser versionado, armazenado ou protegido;
- como organizar sem perder arquivos ou contexto;
- como manter o sistema correto ao longo do tempo.

Ele funciona do zero, mas também pode auditar um projeto maduro. Não pressupõe
software, empresa, marca, idioma ou fornecedor de IA.

## Instalação

O pacote é um plugin Codex com skills portáveis baseadas no formato
`SKILL.md`. As instruções completas estão em
[`INSTALLATION.md`](INSTALLATION.md). Nenhuma API ou conexão MCP é obrigatória
para instalar o núcleo.

## Como começar

Invoque `$athanor` no diretório que deseja compreender. A primeira passagem é
somente leitura. O sistema identifica o tipo de workspace, procura instruções
existentes e evita perguntar algo que possa descobrir com segurança.

O primeiro resultado deve conter:

1. resumo do estado atual;
2. fatos verificados e suas fontes;
3. lacunas sem inferência;
4. riscos imediatos;
5. recomendação de próximo ritual;
6. ações que exigem decisão humana.

## Colaboração e garantia

São dois controles independentes.

### Estilo de colaboração

#### Scribe

Explica conceitos, mostra opções e não altera o projeto sem confirmação.

#### Alchemist

Pesquisa, recomenda e dialoga nas escolhas estruturais. É o modo padrão.

#### Adept

Usa o melhor julgamento disponível, faz poucas perguntas e executa mudanças
locais reversíveis. Não ignora gates de risco.

### Nível de garantia

#### Lean

Mantém verificações proporcionais em trabalho local, reversível e de baixo
risco.

#### Standard

Valida premissas e resultados importantes. É o padrão.

#### Guardian

Adiciona evidência, revisão adversarial e trilha de auditoria. Entra
automaticamente em assuntos sensíveis, independentemente do estilo de
colaboração salvo.

## As fases do trabalho

- **Nigredo — diagnóstico:** tornar o estado real visível.
- **Albedo — estrutura:** separar fontes de verdade e reduzir contradições.
- **Citrinitas — inteligência:** definir agentes, handoffs e capacidades.
- **Rubedo — operação:** executar, integrar, preservar e manter.

Os nomes são uma camada de experiência. Os arquivos e relatórios usam nomes
claros para continuar acessíveis a qualquer pessoa ou IA.

## O que o Athanor diagnostica

Cada domínio recebe um estado:

- `unknown`
- `absent`
- `fragmented`
- `documented`
- `canonical`
- `operational`

A ausência de um arquivo não prova a ausência da capacidade. Um brand book pode
estar dentro de um PDF ainda não inspecionado. O Athanor registra `unknown` ou
`unverified` antes de declarar uma lacuna.

Os domínios incluem identidade, governança, marca, produto ou serviço, público,
design system, operação, marketing, vendas, atendimento, jurídico e privacidade,
finanças, tecnologia, dados, documentação, preservação, ferramentas e
integrações.

Nem todo domínio precisa chegar ao nível máximo. A recomendação é proporcional
ao estágio, risco e objetivo do projeto.

## Organização segura

O fluxo `Solve et Coagula` nunca começa movendo arquivos:

1. inventariar sem ler segredos;
2. compreender objetos e dependências;
3. propor uma taxonomia;
4. gerar um manifesto de movimentos;
5. revisar ambiguidades;
6. obter aprovação;
7. executar por script determinístico;
8. verificar e registrar.

Visão, OCR e extração de texto são usados progressivamente. Arquivos ambíguos
permanecem onde estão e entram em `ORGANIZATION-REVIEW.md`.

O aplicador de plano:

- simula por padrão;
- recusa sobrescrita;
- não aceita caminhos fora da raiz;
- exige aprovação linha a linha;
- exige confirmação de backup;
- registra hash, origem e destino;
- não deleta.

## Git, GitHub e preservação

Git registra história. GitHub hospeda e colabora. Git LFS referencia binários
grandes. Backup permite recuperação. Armazenamento de assets guarda acervos.
Secret managers protegem credenciais.

O Chronicle classifica arquivos em:

- Git normal;
- Git LFS;
- armazenamento de assets;
- backup;
- local ignorado;
- secret manager;
- revisão humana.

Um repositório privado não transforma token, documento pessoal ou banco de
dados em conteúdo seguro para commit.

## Agentes e memória

Agentes são criados por responsabilidade e risco, não por uma lista fixa de
departamentos. Cada agente declara:

- papel e gatilhos;
- fontes em ordem;
- ferramentas verificadas;
- diretrizes;
- travas;
- SOPs;
- formato de entrega;
- handoffs;
- decisões humanas;
- lacunas.

Memória particular é a fonte mais fraca. Fatos compartilhados sobem para a
fonte canônica; decisões entram em `DECISIONS.md`; trabalho entra em
`TASKS.md`; capacidade de ferramenta entra em `TOOLS.md`.

Ao concluir trabalho significativo, o Maintain destila o resíduo: decisão,
fato canônico, comportamento testado de ferramenta, integração, risco, trabalho
futuro, aprendizado particular ou nada. Atividade rotineira não vira memória.

## Integrações

O Athanor começa pelo resultado desejado e compara:

- processo manual assistido;
- conector pronto;
- automação no-code;
- API direta;
- MCP;
- plugin ou app.

Cada opção inclui benefício, pré-requisitos, custo, dificuldade, autenticação,
risco, teste e fallback. Detalhes de fornecedor são verificados em documentação
oficial atual no momento da configuração.

A skill não vem secretamente conectada a contas externas. Quando um objetivo
precisa de uma capacidade ausente, ela deve:

1. explicar por que a conexão é ou não necessária;
2. apontar contas, planos, permissões e revisão de aplicativo exigidos;
3. comparar conector, no-code, API e MCP;
4. guiar a configuração em linguagem compatível com o usuário;
5. testar leitura antes de escrita;
6. registrar apenas nomes de variáveis e metadados seguros;
7. documentar revogação e procedimento manual de fallback.

## Aprovações e segurança

Exigem aprovação humana explícita:

- publicação ou mensagem externa;
- gasto, pagamento ou assinatura;
- deleção ou sobrescrita;
- contrato ou compromisso legal;
- credencial e ampliação de acesso;
- dado pessoal ou de criança;
- mudança em produção;
- Git push ou abertura pública de repositório quando não autorizado.

## Datas

Usar `YYYY-MM-DD` na interface, nos arquivos, nos logs e nos dados estruturados.

## Ajuda

Invoque `$athanor-help` e diga o que está confuso. O módulo deve explicar o
conceito no nível do usuário, relacioná-lo ao projeto atual e sugerir uma única
próxima ação segura.

## Saúde, atualização e continuidade

O Doctor agrega versão da fonte, branch e estado do Git, integridade de links ou
cópias, registros de instalação, cache do Codex e, opcionalmente, a validação de
um Project OS. Ele não produz uma nota universal.

Uma atualização tem duas etapas distintas:

1. atualizar a fonte canônica após revisar o Doctor;
2. atualizar o cache ou a cópia de cada runtime.

O Athanor recusa atualização automática destrutiva. Use somente fast-forward em
uma árvore limpa, revise o changelog e depois execute `refresh`. Cópias recebem
backup; links apenas renovam seu registro; o Codex reinstala o cache. Inicie uma
nova sessão.

Quando o contexto for interrompido, um checkpoint append-only registra objetivo,
IDs de tarefas e decisões, verificação, bloqueios e próxima ação. Ele aponta
para fontes canônicas atuais; não substitui Git ou backup.
