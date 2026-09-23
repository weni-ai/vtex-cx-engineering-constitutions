# VTEX CX Engineering Constitutions

Fonte canônica das **constitutions base** da engenharia VTEX CX. Este
repositório não é a constitution de nenhum projeto: ele guarda as bases que são
combinadas para gerar a constitution de cada projeto, no formato do
[Spec Kit](https://github.com/github/spec-kit).

## Estrutura

```
base-constitution.md                      # engenharia — vale para todos os projetos
backend/base-constitution.md              # específica de backend
frontend/base-constitution.md             # específica de frontend (regras gerais)
frontend-platform/base-constitution.md    # específica de frontend CX Platform (microfrontends)
cloud/base-constitution.md                # específica de cloud
```

O nome do arquivo é sempre `base-constitution.md`. O escopo vem do caminho: a
raiz rege toda a engenharia, cada pasta cobre um domínio.

## Como as bases são combinadas

A constitution de um projeto é a **síntese** da base raiz com a(s) base(s) de
domínio, aplicada ao repositório em questão:

```
base-constitution.md  +  {domínio}/base-constitution.md  →  .specify/memory/constitution.md
```

Precedência:

```
constitution raiz  >  constitution de domínio  >  adaptação do projeto
```

- A raiz define o que toda a engenharia deve cumprir.
- O domínio especializa, sem contradizer a raiz.
- O projeto apenas instancia: stack, pastas, ferramentas, CI, exceções.

A raiz entra **sempre**. As de domínio entram conforme o projeto (um projeto
pode ter mais de um domínio, ex.: monorepo).

## Como consumir

A skill `setup-engineering` do Cursor busca estes arquivos e gera a constitution
do projeto em `.specify/memory/constitution.md`. No repositório do produto:

```
roda setup-engineering para este backend
```

Pré-requisitos no projeto de destino:

- `specify init` já executado (a skill recusa rodar sem `.specify/`)
- `gh` autenticado com acesso a este repositório

Busca manual das bases, se necessário:

```bash
gh repo clone weni-ai/vtex-cx-engineering-constitutions /tmp/constitutions -- --depth 1 --branch main
```

## Como editar as bases

- Escreva princípios **declarativos e testáveis**, com `MUST` / `SHOULD` e
  rationale explícito.
- Não inclua stack, nome de serviço ou caminho de um projeto específico — isso
  pertence à camada do projeto.
- Regra que valha para mais de um domínio pertence à raiz, não duplicada nas
  pastas.
- Mudança em uma base afeta todos os projetos que a usam: abra PR e sinalize o
  impacto na descrição.

Projetos já gerados não são atualizados automaticamente. Rode
`setup-engineering` novamente para trazer as bases novas — as exceções do
projeto ainda válidas são preservadas.
