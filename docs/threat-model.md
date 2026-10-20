| Action category | Examples in AEGIS |
|---|---|
| Code execution | Run generated Python, shell, tests, or repository code |
| Tool creation | Generate, test, register, promote, version, or revoke forged tools |
| External requests | Call web/search, GitHub, HTTP APIs, or other integrations |
| File and repository changes | Write files, modify code, create branches, prepare pull requests |
| Database changes | Insert, update, or delete records; run approved SQL |
| Workflow changes | Start, cancel, resume, retry, or modify a task |
| Model and decision calls | Send data to providers; invoke Jev or fallback decision providers |
| Memory changes | Store task memory, retrieval documents, experiments, and tool history |
| Approval and policy changes | Approve or reject actions; modify permissions or policy configuration |
| Scheduling and automation | Trigger scheduled or event-driven tool calls |
| Deployment and operations | Change deployment configuration, trigger CI/CD, or execute operational actions |
| Security testing | Run authorized red-team checks and security scans |



## Threat Scenarios and Required Controls

### 1. Threat inventory

| ID | Threat scenario | Required controls | Verification |
|---|---|---|---|
| T-01 | Direct or indirect prompt injection attempts to redirect an agent | Treat external content as untrusted data; validate tool arguments; enforce policy independently of model instructions | Prompt-injection test suite |
| T-02 | An agent invokes a tool outside its permissions | Tool allowlists, least-privilege permissions, deterministic policy checks, deny-by-default behavior | Unauthorized tool-call tests |
| T-03 | Generated code performs unintended file, network, or system operations | Isolated sandbox, resource limits, restricted network access, static analysis, disposable execution environments | Sandbox escape and side-effect tests |
| T-04 | A forged tool is promoted before adequate verification | Mandatory sandbox testing, static security analysis, deterministic promotion gate, versioning, risk-based human approval | Failed-candidate and approval-gate tests |
| T-05 | Jev returns an incorrect or manipulated decision | Treat Choice, Score, and Noul outputs as advisory; validate outputs; apply deterministic policy enforcement independently | Low-confidence, adversarial-input, and incorrect-decision tests |
| T-06 | Credentials or sensitive data leak through prompts, tool outputs, or logs | Server-side secret storage, redaction, restricted access, safe logging, controlled provider data exposure | Seeded-secret leakage tests |
| T-07 | An external integration changes production data without authorization | Explicit permissions, risk classification, approval where required, scoped credentials, audit logging | Denied and approved side-effect tests |
| T-08 | A malicious or malformed API response corrupts task state | Schema validation, bounded inputs, safe parsing, transactional persistence, error handling | Malformed-response tests |
| T-09 | A user accesses another user's tasks, approvals, or artifacts | Authentication, authorization checks on every protected resource, tenant isolation where applicable | Cross-user access tests |
| T-10 | Repeated requests exhaust compute, provider budgets, or service capacity | Rate limits, timeouts, bounded retries, concurrency limits, budget enforcement | Load and abuse tests |
| T-11 | An agent repeats a non-idempotent action after a timeout or retry | Idempotency keys where applicable, operation state tracking, duplicate-action prevention | Retry and duplicate-submission tests |
| T-12 | A forged or compromised tool remains available after discovery | Immediate revocation, disabled-tool checks at execution time, version history, incident audit trail | Revocation and subsequent-call tests |
| T-13 | A poisoned retrieval document influences agent behavior | Source-trust metadata, document provenance, retrieval validation, prompt-injection testing | RAG poisoning tests |
| T-14 | An unreviewed agent run triggers deployment or other high-impact operations | Deployment policy gates, explicit authorization, human approval where required, no automatic production deployment from unreviewed runs | Blocked-deployment tests |
| T-15 | Audit records are missing or expose sensitive information | Structured audit events, restricted access, secret redaction, failure monitoring | Audit completeness and redaction tests |

### 2. Non-negotiable enforcement rules

1. Jev is advisory and must never be the sole authorization gate for a side-effecting action.
2. The deterministic Policy Engine makes the binding allow, deny, or approval decision.
3. Forged tools must pass sandbox testing and static security analysis before promotion.
4. A forged tool above the configured risk threshold requires explicit human approval before its first live execution.
5. Candidate tools must not cause real production side effects during sandbox verification.
6. Tool permissions must be checked at execution time, not only when a tool is registered.
7. Revoked tools must be prevented from executing, including through stale references where applicable.
8. Credentials must not be committed to source control or exposed in application logs.
9. Agent-generated content, tool descriptions, retrieved documents, and external responses are untrusted inputs.
10. Security failures must fail closed for protected operations.

### 3. Threat-model assumptions

- All external content and model-generated content may be malicious or incorrect.
- Model confidence does not establish authorization or safety.
- Sandbox isolation must be verified; a separate process alone is not sufficient evidence of isolation.
- Human approval must be bound to a specific action, its parameters, and its risk context.
- Every security-sensitive decision and side effect must produce an appropriately redacted audit record.
- Production credentials and production data must remain outside candidate-tool testing environments.

### 4. Open questions to resolve during architecture design

- What sandbox technology and isolation boundary will be used?
- Which tool categories require mandatory human approval?
- How will authentication, authorization, and tenant isolation be implemented?
- How will audit events be protected against unauthorized modification?
- What are the default resource limits, provider budgets, and retry limits?
- Which external integrations are permitted to access production systems?

These questions remain unresolved until the architecture and configuration are explicitly defined and verified.
