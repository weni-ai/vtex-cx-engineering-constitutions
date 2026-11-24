# AI Models Train Base Constitution

Training-pipeline principles that specialize the root constitution for AI Models team projects whose deliverable is a trained model or training artifact. This is an
intentionally thin first version focused on experiment setup, result
visualization shared with evaluation, trajectory observability, and training
data anonymization. Extend as training practice matures; do not weaken these
gates.

Principles are declarative and testable, stated with `MUST` / `SHOULD` and an
explicit rationale. Stack, tooling, and concrete paths belong to the project
layer, not here.

## Core Principles

### Standardized Experiment Setup
Every training run MUST start from a standardized setup that declares, before
execution: objective, dataset (versioned) and split definition, model
architecture or base checkpoint, hyperparameters, evaluation metrics used during
training, early-stopping or selection rule, cost/compute budget, and random
seeds. The setup MUST be recorded as tracked metadata (e.g. MLflow parameters
and tags), not only in a notebook narrative. An unregistered training run MUST
NOT be treated as evidence for promoting a model.

Rationale: training without a shared setup produces artifacts nobody can compare
or reproduce. Declaring the setup up front is what makes two runs commensurable
and reviewable by someone who did not author them.

### Split Discipline
Train, validation, and test partitions MUST be defined explicitly, MUST be
disjoint, and MUST be versioned alongside the dataset. The partition a record
belongs to MUST be a recorded property of that record, never a function of row
order or of a random draw performed at runtime. When records share an entity
through which information could leak across partitions — the same conversation,
customer, document, or session — the split MUST be performed at the level of
that entity. Results obtained on data used for model or hyperparameter selection
MUST be reported as validation results, not as test results.

Rationale: leakage is the failure mode that produces excellent offline numbers
and a disappointing production model, and it is invisible in the metric by
construction.

### Training Data Anonymization
Data originating from production MUST be anonymized or pseudonymized before it
is used for training, evaluation during training, or prompt/example
construction. Direct identifiers MUST be removed or replaced by opaque
identifiers, and any mapping that permits re-identification MUST be stored
separately and under stricter access than the dataset itself. Personal data MUST
NOT appear in logs, traces, run artifacts, reports, or payloads sent to
third-party providers.

Rationale: a training pipeline is where production data is deliberately copied,
retained, and reprocessed — the largest exposure surface the team owns.
Artifacts outlive the experiment by years. Anonymizing at the entrance is the
only point where the cost is bounded.

### Trajectory-Level Observability
For models that operate in steps (including agentic or multi-stage trainers),
the final metric MUST NOT be the only unit of observability. Every training run
MUST record enough trajectory to diagnose behaviour: step or epoch identifiers,
losses and selection metrics over time, checkpoint references, and — when the
model invokes tools or sub-models during training or validation — the inputs,
outputs, retries, latency, and token consumption of those calls, correlated by a
trace identifier that also appears in structured logs.

Rationale: when only the final score is recorded, a training collapse, a bad
checkpoint, or a silent data bug cannot be located without rerunning an
expensive process. Trajectory artifacts are what make failures diagnosable.

### Standard Result Visualization (Train and Eval)
Every training run MUST emit a machine-readable tabular artifact with a shape
compatible with evaluation reporting: identifiers, per-step or per-checkpoint
metrics, and the aggregates declared in the spec.

- Reports and visualizations MUST be generated from that artifact and MUST NOT
  depend on the in-memory state of the session that produced the run.
- Visualization conventions MUST be shared with evaluation pipelines so training
  and evaluation results can be compared side by side.
- A result that exists only as a chart, a screenshot, or printed notebook output
  MUST NOT be treated as a deliverable.

Rationale: results that live only inside the notebook that produced them cannot
be compared across runs or checked by anyone else. One artifact shape across
training and evaluation is what allows one set of analysis tooling to serve both.

### Tracked and Reproducible Training Runs
Every training run MUST be registered in the project's experiment tracking
system. The registration MUST capture at minimum the code version, dataset
version and split identifiers, model identifiers and hyperparameters, seeds,
environment and dependency versions, and the resulting metrics and artifacts. A
run MUST be reproducible from its recorded metadata alone, without consulting
whoever executed it.

Rationale: training produces many runs that differ in small ways. Tracking is
the only durable record that a promoted model refers to a specific set of
inputs.

## Governance

This constitution governs AI-driven training pipeline work for the data science
team. It is version 0.1.0 by design — expect MINOR additions as practice
stabilizes. Amendments require a PR modifying this file with clear rationale, a
semver bump, and review from at least one maintainer.

**Version**: 0.1.0 | **Ratified**: 2026-11-23 | **Last Amended**: 2026-11-23
