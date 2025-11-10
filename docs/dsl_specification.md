# DSL Specification: Verifiable Processing Pipeline

## Overview

**Prompt:** "Design a DSL that compiles to a verifiable processing pipeline"

### Goal

You will design a small, total, and verifiable domain-specific language (DSL) that describes an information-processing system that takes inputs, performs calculations, and produces outputs. The DSL must be host-language agnostic but come with adapters for at least Python and JavaScript.

### Domain

This domain concerns the generation of dynamic, data-driven dashboards from preprocessed analytical data. The system accepts a prepared Parquet file as input, infers its structure, and defines a set of visualisation specifications that determine how different fields should be aggregated, filtered, and presented. The DSL expresses dashboard layout, chart types, and data bindings declaratively, enabling automatic rendering in frameworks such as Streamlit (for Python) and React/Plotly (for JavaScript). The goal is to make data exploration reproducible, auditable, and language-agnostic while keeping the logic of the visualisation verifiable and portable.

---

## Constraints (Must-Haves)

- **Total semantics**: Every valid program has a defined meaning; no partial evaluation or hidden I/O
- **Closed world**: Reject unknown fields; deterministic output; no network/FS access inside the DSL
- **Canonical form**: The formatter produces one unique, stable representation (key order, whitespace, numeric precision)
- **Static validation**: Exhaustive checks with machine error codes and single-step repair hints
- **Separation of concerns**: Policy tables, units, and factors come from the runtime, not from the DSL document
- **Round-trip**: `parse → canonicalize → parse` must be stable
- **Acyclic execution graph**: If there are dependencies, topological order exists

---

## Deliverables

Return **ONLY** these sections, in the order shown:

### 1. Design Card (YAML)

A one-page spec with:

- `dsl_name`, `purpose`, `non_goals`
- `core_entities` (e.g., Input, Transform, Aggregate, Output)
- `total_semantics` bullets
- `serialization` (YAML with JSON round-trip)
- `versioning` (semver, field name `dsl_version`)
- `canonical_form` rules
- `errors_as` (machine codes + repair hints)
- `targets` (python, javascript)

### 2. Minimal Grammar (PEG/Lark or ANTLR)

Tiny grammar sufficient to parse the DSL (or state "DSL is YAML; grammar omitted" if using schema-first).

### 3. JSON Schema (Closed)

A strict schema (`additionalProperties: false`) for the serialized form, including types, enums, patterns, and requireds.

### 4. Execution Model

- Define the intermediate representation (IR): nodes, edges (if any), evaluation order, and how inputs → calculations → outputs are computed
- Specify unit handling, numeric precision, and determinism guarantees

### 5. Validation Rules

List all structural and semantic checks. For each, provide:

| Field | Description |
|-------|-------------|
| `code` | Machine-readable error code |
| `when` | When this validation triggers |
| `message_template` | Human-readable error message |
| `repair_hint` | Suggested fix |
| `json_pointer_path_example` | Path to the error |

### 6. Golden Examples

Provide three DSL files:

- **`happy_path.yaml`**: Valid, non-trivial example
- **`minimal.yaml`**: Smallest valid example
- **`failing.yaml`**: Invalid; triggers ≥3 distinct error codes

### 7. Adapters (Stubs)

Example typed stubs for host languages (optional):

#### Python (`adapter.py`)

```python
from typing import TypedDict, Iterable, Any

class Violation(TypedDict):
    code: str
    message: str
    path: str
    repair: str

def parse(src: str) -> dict: ...
def canonicalize(model: dict) -> str: ...
def validate(model: dict, policy: dict, factors: dict) -> list[Violation]: ...
def build_ir(model: dict) -> dict: ...
def execute(ir: dict, inputs: dict) -> dict:  # returns outputs
```

#### JavaScript/TypeScript (`adapter.ts`)

```typescript
export interface Violation {
    code: string;
    message: string;
    path: string;
    repair: string;
}

export function parse(src: string): object;
export function canonicalize(model: object): string;
export function validate(model: object, policy: object, factors: object): Violation[];
export function buildIR(model: object): object;
export function execute(ir: object, inputs: object): object;
```

### 8. Formatter Rules

Exact key order, whitespace rules, numeric precision (e.g., 3 decimal places), sorting strategy for arrays (e.g., by `id`), and comment handling.

### 9. Test Vectors

- **Input payloads** (JSON) for `happy_path.yaml`
- **Expected outputs** (JSON)
- **Expected validation violations** (JSON) for `failing.yaml`

### 10. Migration Strategy

- **Semver policy**: Additive defaults
- **Migration approach**: How to emit a `1.x → 2.0` migration map (regex/AST rewrites)
- **Migration function**: `migrate(old) -> new`

---

## Rules for This Task

- Keep the DSL small (≤10 concepts, ≤25 fields total)
- Prefer declarative over procedural
  - No loops or conditionals unless essential
  - If present, they must be finite and statically checkable
- Provide precise error codes (e.g., `MASS_BALANCE_VIOLATION`, `UNKNOWN_FIELD`, `CYCLE_DETECTED`)
- All examples must pass/fail exactly as claimed under the schema and rules
- Do not include hidden reasoning; provide the artifacts only

---

## Return Format

Emit the ten sections with clear `###` headings. Use fenced code blocks with filenames for code.

**Example:**

````yaml
# filename: happy_path.yaml
dsl_version: "1.0.0"
# ...
````

---

## Domain Parameters

Insert a small, concrete scenario here to ground the examples—two inputs, one transform, one aggregation, one output.

**Example:**
“A prepared Parquet file containing anonymized credit card transactions from European customers is loaded as input. The system filters the data to include only transactions within a selected time window, computes a fraud-likelihood score using an existing classification model, and aggregates detection metrics such as the proportion of suspected frauds and the Area Under the Precision-Recall Curve (AUPRC). The output is a Streamlit dashboard presenting a time-series chart of transaction volume, a precision-recall curve visualizing model performance, and a summary table highlighting high-risk transactions.”
