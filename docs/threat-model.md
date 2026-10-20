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



## 5. Jev Decision Layer and Tool Forge Specific Risks

### 5.1 Jev Decision Layer

| ID | Risk | Worst-case failure | Required gate or mitigation |
|---|---|---|---|
| J-01 | Overconfident incorrect decision | A wrong classification influences routing, scoring, or an action pre-screen | Confidence thresholds, held-out calibration tests, and escalation to System 2 or human review |
| J-02 | Adversarial state manipulation | Crafted state data causes Jev to produce a misleading answer | Validate and bound state inputs; treat supplied state as potentially adversarial; enforce deterministic policy independently |
| J-03 | False low-risk classification | Jev classifies a dangerous action as safe | Policy Engine independently evaluates the action and makes the binding allow/deny/approval decision |
| J-04 | Provider outage or access interruption | Jev calls fail and interrupt task execution | Swappable DecisionProvider interface and tested LocalDecisionProvider fallback |
| J-05 | Confidence threshold misconfiguration | Too many unsafe decisions are accepted, or necessary escalations are missed | Configurable thresholds, conservative defaults, calibration evaluation, and versioned configuration |
| J-06 | Unreliable decision telemetry | Incorrect conclusions are drawn about agreement, calibration, latency, or cost | Log state summary, question type, answer, confidence, escalation, outcome, and agreement |
| J-07 | Proprietary provider assumptions | Provider changes break the rest of the application | Keep Jev behind the DecisionProvider interface; do not depend on undocumented internals |
| J-08 | Unverified performance claims | Project reports claim speed or cost improvements not measured on AEGIS workloads | Compare measured latency and cost against an LLM-only baseline |

**Jev enforcement rules**

1. Jev is advisory; it never replaces deterministic Policy Engine enforcement or required human approval.
2. Low confidence must trigger the configured escalation or fallback path.
3. A provider failure must not silently convert an uncertain decision into permission to execute.
4. Decision logs must support independent calibration and agreement analysis.
5. Evaluate Jev on held-out labeled data and crafted/adversarial states.
6. Measure actual AEGIS latency and cost; do not present provider-reported gains as AEGIS results.

### 5.2 Tool Forge

| ID | Risk | Worst-case failure | Required gate or mitigation |
|---|---|---|---|
| F-01 | Malicious candidate generation | Generated code steals secrets, modifies files, or attempts network access | Isolated sandbox, restricted capabilities, resource limits, and static security analysis |
| F-02 | Unsafe candidate passes incomplete tests | A vulnerable tool is promoted and executes against real systems | Independent sandbox tests, static analysis, deterministic promotion gate, and required approval |
| F-03 | Capability-gap prompt injection | Untrusted task descriptions or API schemas manipulate generated code | Treat descriptions and schemas as untrusted; validate generated code and tool contracts independently |
| F-04 | Jev incorrectly pre-screens a candidate | A risky candidate is treated as low risk | Jev pre-screen is advisory; deterministic security and policy gates remain mandatory |
| F-05 | Live side effects during candidate testing | Candidate code modifies production data or calls a live endpoint before approval | Mock or staging targets, sandbox isolation, deny-by-default network access, and no production credentials |
| F-06 | Forged tool permission escalation | A candidate requests broader privileges than the task requires | Least-privilege permissions, schema validation, policy-configured risk tiers, and execution-time authorization |
| F-07 | Unbounded forging loop | Repeated failed candidates exhaust compute, time, or provider budgets | Hard candidate-attempt, sandbox-time, retry, and task-budget limits |
| F-08 | Compromised or vulnerable promoted version | A previously trusted tool continues causing harm | Version history, revocation, disabled-tool checks at execution time, and incident audit records |
| F-09 | Unsafe promotion or approval bypass | Candidate code reaches the trusted registry without satisfying required gates | Explicit promotion state machine; deny-by-default transitions; approval bound to the candidate version and risk context |
| F-10 | Incomplete provenance | The team cannot reconstruct how a tool was generated, tested, or promoted | Record source gap, candidate version, schema, test results, static-analysis results, policy outcome, approval, and promotion/revocation history |

**Tool Forge enforcement rules**

1. Candidate generation does not grant execution privileges.
2. Candidate tools must be tested in isolation before promotion.
3. Static security analysis and deterministic policy checks are mandatory.
4. Human approval is required wherever the configured risk policy requires it.
5. Jev cannot waive sandbox, policy, or approval requirements.
6. Candidate generation and sandbox execution must have hard resource limits.
7. Promoted tools must be versioned, auditable, and revocable.
8. Unsafe-promotion rate is a critical evaluation metric; the target is zero.

### 5.3 Verification requirements

The following tests must exist before the corresponding capabilities are considered complete:

- Force Jev to return a low-risk answer for a known high-risk action; verify that the Policy Engine still blocks or requires approval.
- Simulate Jev provider failure; verify that the configured local fallback works.
- Supply a crafted/adversarial state; record the result and verify escalation behavior where required.
- Attempt to promote a candidate that fails sandbox tests or static analysis; promotion must be rejected.
- Attempt live side effects from candidate-tool testing; the sandbox and network controls must prevent them.
- Exhaust the configured Tool Forge candidate-attempt limit; verify that forging stops.
- Revoke a promoted tool; verify that subsequent execution attempts are denied.
- Verify that the decision log and tool-version history contain the records needed for security review and evaluation.

### 5.4 Outstanding implementation decisions

The following remain design decisions until explicitly specified and tested:

- Sandbox technology and isolation strength.
- Risk tiers and the actions requiring mandatory approval.
- Jev confidence thresholds and escalation policy by decision type.
- Local fallback behavior when the provider and fallback are both unavailable.
- Tool Forge candidate, time, and budget limits.
- Promotion-state transitions and approval binding.
- Audit-record integrity and retention requirements.

No control described here should be considered implemented solely because it is documented.


### Tool Forge Audit-Linkage Invariant

- Before a tool version exists, candidate lifecycle events may reference the candidate only.
- Once a forged tool version exists, events concerning that version must reference both the originating candidate and the resulting tool version.
- Events for developer-registered tools may reference a tool version without a Tool Forge candidate.
- The application must verify that a referenced tool version belongs to the referenced candidate before writing an audit event.
- Audit events must be append-only. Relevant validation, approval, promotion, rejection, and revocation actions must create durable event records rather than overwrite prior history.

These invariants must be enforced and tested in the Tool Forge audit and promotion services. Database-level protections must be evaluated during database implementation.
