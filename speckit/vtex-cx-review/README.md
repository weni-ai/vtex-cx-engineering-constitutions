# Extension `vtex-cx-review`

Extension do [Spec Kit](https://github.com/github/spec-kit) que adiciona a etapa
de **revisão adversarial de código** ao Golden Path VTEX CX, logo após o
`/speckit-converge`, aplicando um núcleo genérico e lentes específicas por
domínio (`backend`, `frontend` e `frontend-platform`) ancoradas na constitution
do repositório.

## Por que ela é separada do `speckit-converge`

O `speckit-converge` (comando core do Spec Kit) e o `vtex-cx-review` respondem
perguntas complementares usando o mesmo contrato de saída:

| Etapa | Pergunta que responde | O que inspeciona | O que escreve |
|-------|-----------------------|------------------|---------------|
| `/speckit-converge` | *"Construímos tudo o que `spec.md`, `plan.md` e `tasks.md` pediram?"* | Apenas os arquivos citados nos artefatos (sem `git`) | `## Phase N: Convergence` em `tasks.md` |
| `/speckit-cx-review` | *"O que realmente mudou no `git` é seguro, isolado entre escopos, performático e provado por testes reais?"* | `git diff` completo + working tree + irmãos do módulo + testes/lint | `## Phase N: Review` em `tasks.md` |

Nenhum dos dois edita código da aplicação, faz `git add`/`git commit` ou abre
PR: ambos apenas acrescentam tasks rastreáveis ao final do `tasks.md` para que o
`/speckit-implement` execute a correção em contexto separado da avaliação.

O ciclo completo no **SDD Full** fica:

```
implement  →  converge  →  implement (até Converged)  →  vtex-cx-review  →  implement / converge / review (até Review passed)
```

No **SDD Lite** (onde há `spec.md`, mas não há `plan.md` nem `tasks.md`), o
comando roda em modo **somente relatório**: executa a mesma barra sobre o `git
diff` + `spec.md` + `constitution.md` sem criar um `tasks.md` artificial.

## Arquitetura: núcleo genérico + lentes por domínio

Espelha exatamente a hierarquia das constitutions deste repositório:

```
.specify/memory/constitution.md   (autoridade normativa: raiz > domínio > projeto)
  + lenses/core.md                (sempre ativa — agnóstica de stack)
  + lenses/backend.md             (quando o repo ou o diff toca backend)
  + lenses/frontend.md            (quando o repo ou o diff toca frontend / frontend-platform)
```

Repositórios de outros domínios (por exemplo, cloud) rodam apenas com
`lenses/core.md`; a constitution do repositório continua sendo a autoridade
normativa da revisão.

O script `scripts/python/resolve_review_context.py` resolve automaticamente os
domínios ativos somando:

1. os domínios declarados na proveniência de `.specify/memory/constitution.md` e
   no cabeçalho de `spec.md` (mais detecção de `@weni/unnnic-system` para
   `frontend-platform`); e
2. os domínios inferidos pelos caminhos reais do `git diff` — o que permite que
   monorepos ativem apenas as lentes pertinentes ao PR (ou ambas, quando um PR
   atravessa `backend/` e `frontend/`).

### Regra de ouro: nenhuma regra existe apenas na lente

As lentes (`lenses/*.md`) **não inventam obrigações próprias**: toda regra
normativa (`MUST` / `SHOULD`) vive nas `base-constitution.md` (raiz ou domínio),
para que `/speckit-specify`, `/speckit-plan`, `/speckit-implement` e
`/speckit-converge` conheçam exatamente a mesma barra antes da revisão. As
lenses contêm apenas **como auditar o `git diff`** contra esses princípios
(onde olhar, procedimento FIIR, tabelas de evidência e severidade). Cada linha
cita o princípio pelo nome e diz onde procurar; o requisito em si (limites,
listas de valores permitidos ou proibidos, convenções de nome) só existe no
texto da constitution, para que mudar a regra nunca exija mudar a lente.

Lentes acrescentam profundidade, não cobertura:

- **Varredura residual**: todo princípio da constitution do repositório que
  nenhuma linha de lente cita (inclusive princípios da camada do projeto ou
  adicionados depois das lentes) é revisado direto pelo texto, com a escala de
  impacto. Um princípio novo é revisado desde o primeiro dia, sem tocar nas
  lentes.
- **Linhas órfãs são puladas**: se uma linha cita um princípio que não existe
  na constitution do repositório (renomeado, removido ou emendado pelo
  projeto), a linha não é aplicada e vira uma observação `LOW` apontando o
  desalinhamento, em vez de aplicar uma regra que já não existe.

Mapa atual das lentes:

- **`lenses/core.md` (`base-constitution.md`)**: auditoria do `git diff` para
  `Contained Changes`, `No Silent Divergence`, `Specification Traceability`,
  `Versioned Contracts`, `Changelog Maintenance`, `Security and Secrets`,
  `Observability`, heurísticas de diff para `Proportional Design` e `Code
  Clarity and Language`, procedimento FIIR de integridade de ramos e detecção de
  testes tautológicos (`Verification Integrity`).
- **`lenses/backend.md` (`backend/base-constitution.md`)**: tabelas de *Threat
  Pass*, *Cross-Scope Pass* e *Entry-Point Performance*, gatilhos condicionais e
  matriz de testes cobrindo `Never Trust the Client`, `Explicit, Scoped
  Authorization`, `Fail Gracefully and Predictably`, `Bounded Retry Over REST`, `Scalability and
  Peak Load`, `Backward-Compatible Data Evolution`, `Diagnosable Errors`, `Tests
  Exercise Flows` e `Explicit Over Clever`.
- **`lenses/frontend.md` (`frontend/` + `frontend-platform/`)**: tabelas de
  *Client Trust Pass* (`Client Trust Boundary`), *Async State & Boundaries*
  (`Async State Correctness`, `API Integration`, `API and Data Boundaries`,
  `State Management`), *Rendering/Bundle/Lifecycle* (`Performance`), mapa de
  severidade dos princípios de UI e CX Platform (`@weni/unnnic-system`,
  `Isolation`, `Communication`) e matriz de testes (`Testing`).

### Severidade

O verbo modal decide se um achado é acionável; o impacto decide a severidade:

- violar um `MUST`, ou um `SHOULD` sem justificativa, gera achado de no mínimo
  `MEDIUM` (um `SHOULD` nunca passa de `MEDIUM`);
- a severidade indicada na linha da lente que cobre o achado é a que vale;
- para o que nenhuma lente cobre, a escala é por impacto: `CRITICAL` para
  explorável, irreversível ou quebra de contrato; `HIGH` para comportamento
  incorreto em operação normal ou verificação quebrada; `MEDIUM` para
  manutenção e escopo, sem efeito em runtime;
- `LOW` é observação sem âncora na constitution ou fora do fluxo alterado e
  nunca vira task.

## Gates de execução

1. **Constitution preenchida**: recusa rodar se `.specify/memory/constitution.md`
   não existir ou ainda for o template padrão do `specify init` (pede
   `setup-engineering`).
2. **Zero tasks abertas (SDD Full)**: recusa rodar enquanto houver `- [ ]` em
   aberto no `tasks.md` (sejam tasks iniciais, de `Convergence` ou de um
   `Review` anterior), evitando revisar código sabidamente incompleto. Para uma
   inspeção intermediária sem escrita em `tasks.md`, passe `--allow-open-tasks`.
3. **Diff não vazio**: se não houver arquivos de código/config/teste alterados
   fora de `specs/` e `.specify/`, encerra sem ruído.

## Hook `after_converge`

A extension registra `speckit.vtex-cx-review.run` em `hooks.after_converge` com
`optional: true`. Assim, sempre que o `/speckit-converge` termina:

- se ainda houve `tasks_appended`, o desenvolvedor segue direto para o
  `/speckit-implement` sem disparo prematuro;
- quando o converge reporta `✅ Converged`, o comando já exibe o atalho pronto
  para disparar a revisão adversarial (na mesma sessão ou numa sessão limpa de
  agente, recomendada para evitar viés de quem implementou).

Times que quiserem tornar o disparo automático após todo converge podem alterar
`optional: false` em `.specify/extensions.yml` — o gate de tasks abertas impede
que a revisão rode caso o converge tenha acabado de abrir pendências.

## Instalação num repositório

Pré-requisitos: `specify init`, constitution gerada por `setup-engineering` e
preset `vtex-cx-engineering` instalado.

A partir de um clone deste repositório:

```bash
git clone --depth 1 https://github.com/weni-ai/vtex-cx-engineering-constitutions /tmp/vtex-cx
specify extension add --dev /tmp/vtex-cx/speckit/vtex-cx-review
```

O `extension add` copia `commands/`, `lenses/` e `scripts/` para
`.specify/extensions/vtex-cx-review/`, registra o hook em
`.specify/extensions.yml` e materializa o comando canônico e o alias curto na
integração ativa:

- **Skills mode** (ex.: Cursor `cursor-agent`): `/speckit-cx-review` (alias) e
  `/speckit-vtex-cx-review-run` (canônico)
- **Command mode**: `/speckit.cx-review` (alias) e `/speckit.vtex-cx-review.run`
  (canônico)

## Verificação

```bash
specify extension list
specify extension info vtex-cx-review
```

## Manutenção

Altere sempre aqui, nunca em `.specify/extensions/vtex-cx-review/` nem em
`.cursor/skills/` do repositório consumidor (ambos são artefatos instalados).
Evolua regras normativas primeiro nas `base-constitution.md` correspondentes e
mantenha as lentes como operacionalização verificável dessas regras:

- adicionar ou alterar o conteúdo de um princípio não exige mudar lentes; a
  varredura residual e o texto da constitution cobrem a mudança;
- renomear ou remover um princípio exige atualizar as linhas que o citam, senão
  elas passam a ser puladas;
- ao escrever uma linha, descreva onde olhar e como graduar, nunca o valor da
  regra (números, listas permitidas ou proibidas, prefixos, códigos de status).

Atualize `extension.version` em SemVer a cada mudança.
