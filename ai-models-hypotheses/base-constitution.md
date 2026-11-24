# AI Models Hypotheses Base Constitution

Hypothesis-validation principles that specialize the root constitution for AI Models team experiments. The goal is evidence that can be accepted or rejected under rules
declared before the run — not post-hoc rationalization of a preferred outcome.

Principles are declarative and testable, stated with `MUST` / `SHOULD` and an
explicit rationale. Stack, tooling, and concrete paths belong to the project
layer, not here — except where a tracking system (e.g. MLflow) is named as the
required evidence store.

## Core Principles

### Standardized Experiment Setup
Every hypothesis experiment MUST start from a standardized setup that declares,
before execution: the hypothesis statement, primary metric, baseline, dataset
(versioned), model/prompt configuration, decision rule, statistical test, cost
budget, and random seeds. The setup MUST be recorded as tracked metadata, not
only in a document. Ad-hoc notebook runs that skip this setup MUST be labelled
exploratory and MUST NOT be reported as decision evidence.

Rationale: without a shared setup, each experiment invents its own notion of
"done" and results cannot be compared. Declaring the full setup up front is what
makes two runs commensurable and reviewable by someone who did not author them.

### Prior Art Before the Experiment
Before a hypothesis is tested with a new model, metric, or technique, the
current state of the art for that problem MUST be surveyed and recorded in the
engineering or experiment spec. The record MUST name the approaches considered,
the baseline each one establishes, and why the chosen approach was preferred. A
new approach MUST be measured against at least one established baseline;
"it performs well" MUST NOT be stated without saying well compared to what.

Rationale: reading what is already known costs hours; rediscovering months later
that a simpler documented method wins costs the whole project. Requiring a
baseline turns a subjective quality claim into a number someone else can
reproduce and challenge.

### Measurement Derives from Product Spec
Every metric used to accept or reject a hypothesis MUST trace to a success
criterion of a pinned product spec (or to a binding architecture decision), each
pinned by commit or tag. A metric that no inherited criterion asks for MUST NOT
be promoted to a decision metric. A success criterion that no metric covers MUST
be raised as a gap rather than left unmeasured.

Rationale: experiment pipelines can produce unbounded plausible numbers. Without
a declared link back to product intent, the team optimizes whatever was easiest
to compute and discovers at review that it measured something nobody asked about.

### Hypotheses and Decision Rules Declared Before the Run
Every experiment MUST declare, before it executes, the hypothesis being tested,
the primary metric, and the decision rule that accepts or rejects it —
direction, threshold, and the minimum difference considered meaningful — plus
the statistical test that will be applied. An analysis whose decision rule was
chosen after the results were seen MUST be labelled exploratory and MUST NOT be
reported as evidence until a new run confirms it under a pre-declared rule.

Rationale: once results are visible there is always a slice, metric, or
threshold under which the preferred option wins. Fixing the rule beforehand is
what distinguishes a finding from a rationalization.

### Statistical Tests for Model Comparisons
A comparison between two models, prompts, or configurations MUST NOT be decided
on point estimates alone. It MUST report the sample size, an uncertainty
interval for the primary metric, and the size of the observed difference.
Comparisons SHOULD be paired on the same records, and the test applied MUST be
appropriate to the metric's nature — proportion, continuous score, or ranking.
When the difference falls within the uncertainty interval, the result MUST be
reported as inconclusive, never as a win.

Rationale: evaluation sets are small and model outputs are noisy. Shipping on a
few points of difference that sit inside uncertainty means shipping on noise.

### Reproducibility of Experiments
Every hypothesis run MUST be fully reproducible given the same inputs. Dataset
versions MUST be pinned. Hyperparameters, model identifiers, prompt templates,
scoring thresholds, seeds, environment, and dependency versions MUST be logged
with the run. A run MUST be reproducible from its recorded metadata alone,
without consulting whoever executed it.

Rationale: model work produces many runs that differ in small ways, and human
memory for which configuration produced which number fails within days.
Reproducibility from metadata is the testable form of the rule.

### Final Results Live in MLflow
Final results that support a hypothesis decision MUST be registered in MLflow
(or the project's designated tracking system equivalent). An unregistered run
MUST NOT be used as evidence. Registration MUST capture parameters, metrics,
artifacts, and tags sufficient to reconstruct the decision. Intermediate
exploratory charts MAY exist outside MLflow; decision artifacts MUST NOT.

Rationale: results that live only in notebooks, screenshots, or chat threads
cannot be audited or compared. MLflow is the durable evidence store the team
already uses for evaluation lineage; hypothesis decisions need the same bar.

### Standardized Sampling
Sampling procedures for experiment datasets MUST be declared and versioned:
population definition, inclusion/exclusion rules, sample size rationale, and
whether the sample is stratified, paired, or random. Sampling code MUST be under
version control. A sample redrawn at runtime without a recorded seed or snapshot
MUST NOT be used for a decision run.

Rationale: an undocumented sample is an invisible degree of freedom. Standardizing
sampling is what keeps "we tried it on some data" from becoming an unchallengeable
claim.

### Standardized EDA Before Modelling Decisions
Before a dataset is used to justify a modelling or hypothesis decision,
exploratory data analysis MUST be performed and recorded against a shared EDA
checklist covering at minimum completeness, duplication, target validity, target
distribution, and obvious leakage risks. The resulting profile MUST be persisted
as a run artifact. A dataset that violates a declared quality threshold MUST
block the decision run until the data is corrected or the threshold is amended
in the spec.

Rationale: models absorb whatever the data contains. Quality problems arrive as
quietly wrong metrics, not as hard failures. Declared EDA gates convert "the
data looked fine" into a check that fails loudly and leaves an artifact.

### Declared Token and Cost Budgets
Any hypothesis run that calls a paid model API MUST declare an expected token
and cost budget before it executes. Actual consumption MUST be measured and
recorded alongside the estimate. A run that exceeds its declared budget MUST
stop or require an explicit override; it MUST NOT continue silently. The basis
of the estimate — unit prices and expected call volume — MUST be recorded so it
can be audited against observed consumption.

Rationale: cost is dominated by a multiplication that is easy to get wrong by an
order of magnitude (rows × turns × scorers × retries). Declaring the estimate
before the run turns that multiplication into something a reviewer can check in
seconds.

### Regular Use of Designated APIs
When an experiment invokes agents or model APIs, it MUST use the project's
designated integration surfaces (for example the OpenAI Agents SDK for agent
runs, and the approved routing layer for model selection). Direct provider
clients MUST NOT be introduced for a one-off experiment path that bypasses
shared retry, telemetry, and cost accounting.

Rationale: hypothesis work that invents a parallel API path produces evidence
that cannot be compared to production-faithful evaluation or to other
experiments on the team.

## Governance

This constitution governs AI-driven hypothesis validation for the data science
team. Amendments require a PR modifying this file with clear rationale, a
semver bump (MAJOR for principle removal/redefinition, MINOR for new
principles, PATCH for clarifications), and review from at least one maintainer.

**Version**: 0.1.0 | **Ratified**: 2026-11-23 | **Last Amended**: 2026-11-23
