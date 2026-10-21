# AEGIS

**Agentic AI Engineering, Governance, Intelligence, and Security Platform**

AEGIS is a full-scope agentic AI engineering platform designed around
agent orchestration, governed tool execution, evaluation, security, and
the Jev Decision Layer and Tool Forge capabilities.

## Project status

The project is in its foundation and architecture phase. The repository
contains initial design artifacts and a monorepo directory skeleton.
Directories do not imply that their corresponding features are implemented.

## Architecture areas

- `apps/` — web and API applications
- `agents/` — specialized agent roles
- `core/` — orchestration, memory, policy, registry, and state
- `llm/` — language-model provider integrations
- `decision/` — decision primitives, Jev, and local fallback
- `tools/` — integrations and executable tools
- `tool_forge/` — candidate tool drafting, analysis, and promotion gates
- `evaluation/` — agent, retrieval, security, benchmark, and calibration evaluation
- `sandbox/` — isolated execution infrastructure
- `workers/` — background processing
- `tests/` — unit, integration, evaluation, Tool Forge, and decision tests
- `docs/` — architecture and project documentation
- `scripts/` — development and maintenance scripts
- `docker/` — container and local environment configuration

## Design artifacts

- `schema_v1.sql` — database schema design draft; not yet validated against PostgreSQL
- `api-contracts.yaml` — OpenAPI API contract draft
- `docs/threat-model.md` — security threat model

## Development principles

- Enforce authorization and policy checks in deterministic application code.
- Treat model-generated decisions as advisory unless explicitly governed by policy.
- Require appropriate approval, sandboxing, screening, and auditability for risky tool operations.
- Validate database changes, API contracts, evaluations, and security controls throughout development.

## Project scope

AEGIS is intended to be built in full according to its build plan and project
specification. The directory structure is a starting point, not a declaration
that features are complete.

## Current development status

See the GitHub Project roadmap and the project documentation for task status
and planned milestones.
