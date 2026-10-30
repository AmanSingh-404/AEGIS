import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import React, { useState } from 'react';
import { Badge } from '../../components/common/Badge';
export const ForgeSection = () => {
    const [activeTab, setActiveTab] = useState('code');
    const [activeStepIndex, setActiveStepIndex] = useState(2);
    const steps = [
        'Describe',
        'Generate',
        'Sandbox test',
        'Validate',
        'Policy decision',
        'Human review when required',
        'Promote'
    ];
    return (_jsx("section", { className: "tint", id: "forge", style: { padding: '96px 0' }, children: _jsxs("div", { className: "wrap", children: [_jsxs("div", { children: [_jsx("h2", { style: { fontSize: 'clamp(34px, 5vw, 64px)', maxWidth: '18ch' }, children: "Create new capabilities. Verify before promotion." }), _jsx("p", { className: "lead", children: "When the Critic finds a capability gap, Tool Forge drafts a candidate tool. A forged tool never runs with real side effects before it passes sandbox testing, and never becomes trusted by itself." })] }), _jsx("div", { className: "steps", "aria-label": "Tool Forge pipeline", children: steps.map((st, i) => (_jsx("span", { className: `${i === activeStepIndex ? 'on' : ''} ${i === 5 ? 'hr' : ''}`, onClick: () => setActiveStepIndex(i), title: "Click to view stage status", children: st }, st))) }), _jsxs("div", { className: "panel ws", children: [_jsxs("div", { children: [_jsxs("div", { className: "tabs", role: "tablist", children: [_jsx("button", { type: "button", role: "tab", "aria-selected": activeTab === 'code', onClick: () => setActiveTab('code'), children: "Draft" }), _jsx("button", { type: "button", role: "tab", "aria-selected": activeTab === 'schema', onClick: () => setActiveTab('schema'), children: "Schema" })] }), _jsx("pre", { className: "mono", children: activeTab === 'code'
                                        ? `# gap: no tool for internal billing API
# origin=forged  status=sandboxed  (demo)
def fetch_billing(quarter: str) -> dict:
    """Read-only client. Permission: network
    (billing.internal, GET only)."""
    resp = http.get(f"{BASE}/invoices",
                    params={"q": quarter})
    return validate(resp.json(), Schema)`
                                        : `input_schema:  { quarter: string }
output_schema: { invoices: Invoice[] }
permissions:   [network: billing.internal GET]
risk_level:    high (needs approval)
origin:        forged   version: v1` })] }), _jsxs("div", { children: [_jsxs("div", { className: "row", children: [_jsx("span", { children: "Sandbox tests" }), _jsx(Badge, { variant: "ok", text: "8 of 8 passed" })] }), _jsxs("div", { className: "row", children: [_jsx("span", { children: "Static analysis" }), _jsx(Badge, { variant: "ok", text: "no hard-fail" })] }), _jsxs("div", { className: "row", children: [_jsx("span", { children: "Jev pre-screen (advisory)" }), _jsx(Badge, { variant: "run", text: "Risk 0.31" })] }), _jsxs("div", { className: "row", children: [_jsx("span", { children: "Policy decision" }), _jsx(Badge, { variant: "wait", text: "Needs approval" })] }), _jsxs("div", { className: "row", children: [_jsx("span", { children: "Version" }), _jsx("span", { className: "mono", children: "v1 \u00B7 revocable" })] }), _jsx("p", { className: "help", style: { marginTop: '14px' }, children: "Illustrative demo data. Jev never writes the code or makes the promotion decision." })] })] })] }) }));
};
