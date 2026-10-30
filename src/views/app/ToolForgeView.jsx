import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { Badge } from '../../components/common/Badge';
export const ToolForgeView = () => {
    const { setRoute, openModal, billingApproved, promoteTool, showToast } = useApp();
    const [activeTab, setActiveTab] = useState('code');
    const [sandboxRunning, setSandboxRunning] = useState(false);
    const [testResults, setTestResults] = useState([
        { name: 'valid quarter', pass: true },
        { name: 'empty response', pass: true },
        { name: 'malformed JSON', pass: true },
        { name: 'timeout handling', pass: true }
    ]);
    const tabs = [
        { key: 'code', label: 'Generated code' },
        { key: 'schema', label: 'Schema' },
        { key: 'sandbox', label: 'Sandbox' },
        { key: 'static', label: 'Static analysis' },
        { key: 'history', label: 'History' }
    ];
    const handleRunSandbox = () => {
        setSandboxRunning(true);
        showToast('Executing isolated Docker worker sandbox tests...');
        setTimeout(() => {
            setSandboxRunning(false);
            showToast('All 8 of 8 sandbox tests passed successfully!');
        }, 1200);
    };
    const handlePromote = async () => {
        await promoteTool('billing_api_client');
        setRoute('tools');
    };
    return (_jsxs(_Fragment, { children: [_jsxs("div", { className: "head", children: [_jsxs("div", { children: [_jsx("div", { className: "crumb", children: "Demo workspace / Tool Forge" }), _jsx("h1", { children: "Tool Forge" }), _jsx("p", { children: "Draft, test, validate and promote new tools. Nothing runs live without passing every gate." })] }), _jsx("div", { children: _jsx("button", { type: "button", className: "btn p", onClick: () => openModal('gap'), children: "Describe a new tool" }) })] }), _jsxs("div", { className: "g g2", children: [_jsxs("div", { className: "card", children: [_jsxs("div", { style: { display: 'flex', justifyContent: 'space-between', alignItems: 'center' }, children: [_jsxs("h3", { children: ["billing_api_client ", _jsx("span", { className: "mono", children: "v1 \u00B7 candidate" })] }), _jsx("button", { type: "button", className: "btn", style: { height: '30px', fontSize: '12px' }, onClick: handleRunSandbox, disabled: sandboxRunning, children: sandboxRunning ? 'Running sandbox...' : '▶ Re-run sandbox' })] }), _jsx("div", { className: "tabs", role: "tablist", style: { marginTop: '12px' }, children: tabs.map(t => (_jsx("button", { type: "button", role: "tab", "aria-selected": activeTab === t.key, onClick: () => setActiveTab(t.key), children: t.label }, t.key))) }), _jsxs("div", { children: [activeTab === 'code' && (_jsx("pre", { className: "mono", children: `def fetch_billing(quarter: str) -> dict:
    """Read-only client. Network: billing.internal GET."""
    resp = http.get(f"{BASE}/invoices", params={"q": quarter})
    return validate(resp.json(), InvoiceSchema)` })), activeTab === 'schema' && (_jsx("pre", { className: "mono", children: `input_schema:  { quarter: string }
output_schema: { invoices: Invoice[] }
permissions:   network(billing.internal, GET)
risk_level:    high
timeout:       10s   origin: forged` })), activeTab === 'sandbox' && (_jsxs(_Fragment, { children: [_jsx("div", { className: "tw", children: _jsxs("table", { children: [_jsx("thead", { children: _jsxs("tr", { children: [_jsx("th", { scope: "col", children: "Test" }), _jsx("th", { scope: "col", children: "Result" })] }) }), _jsx("tbody", { children: testResults.map((t, i) => (_jsxs("tr", { children: [_jsx("td", { children: t.name }), _jsx("td", { children: _jsx(Badge, { variant: t.pass ? 'ok' : 'bad', text: t.pass ? 'Pass' : 'Fail' }) })] }, i))) })] }) }), _jsx("p", { className: "help", children: "Ran in isolated Docker container worker against mock endpoints." })] })), activeTab === 'static' && (_jsx("div", { className: "tw", children: _jsxs("table", { children: [_jsx("thead", { children: _jsxs("tr", { children: [_jsx("th", { scope: "col", children: "Check" }), _jsx("th", { scope: "col", children: "Result" })] }) }), _jsxs("tbody", { children: [_jsxs("tr", { children: [_jsx("td", { children: "Dangerous imports" }), _jsx("td", { children: _jsx(Badge, { variant: "ok", text: "None found" }) })] }), _jsxs("tr", { children: [_jsx("td", { children: "Network scope" }), _jsx("td", { children: _jsx(Badge, { variant: "ok", text: "Single host" }) })] }), _jsxs("tr", { children: [_jsx("td", { children: "Secret handling" }), _jsx("td", { children: _jsx(Badge, { variant: "ok", text: "Env only" }) })] }), _jsxs("tr", { children: [_jsx("td", { children: "Injection patterns" }), _jsx("td", { children: _jsx(Badge, { variant: "ok", text: "None found" }) })] })] })] }) })), activeTab === 'history' && (_jsx("div", { className: "tw", children: _jsxs("table", { children: [_jsx("thead", { children: _jsxs("tr", { children: [_jsx("th", { scope: "col", children: "Version" }), _jsx("th", { scope: "col", children: "Event" })] }) }), _jsxs("tbody", { children: [_jsxs("tr", { children: [_jsx("td", { children: "v1" }), _jsx("td", { children: "Drafted, sandboxed, pending approval" })] }), _jsxs("tr", { children: [_jsx("td", { children: "\u2014" }), _jsx("td", { children: "Earlier: fx_rate_fetch v2 promoted" })] }), _jsxs("tr", { children: [_jsx("td", { children: "\u2014" }), _jsx("td", { children: "Earlier: csv_dedupe rejected" })] })] })] }) }))] })] }), _jsxs("div", { className: "card", children: [_jsx("h3", { children: "Gate status" }), _jsxs("div", { className: "row", children: [_jsx("span", { children: "Sandbox" }), _jsx(Badge, { variant: "ok", text: "Passed" })] }), _jsxs("div", { className: "row", children: [_jsx("span", { children: "Static analysis" }), _jsx(Badge, { variant: "ok", text: "Passed" })] }), _jsxs("div", { className: "row", children: [_jsx("span", { children: "Jev pre-screen (advisory)" }), _jsx(Badge, { variant: "run", text: "Risk 0.31" })] }), _jsxs("div", { className: "row", children: [_jsx("span", { children: "Policy decision" }), _jsx(Badge, { variant: "wait", text: "Needs approval" })] }), _jsxs("div", { className: "row", children: [_jsx("span", { children: "Human review" }), billingApproved === true ? (_jsx(Badge, { variant: "ok", text: "Approved" })) : billingApproved === false ? (_jsx(Badge, { variant: "bad", text: "Rejected" })) : (_jsx(Badge, { variant: "wait", text: "Pending" }))] }), _jsxs("div", { className: "row", children: [_jsx("span", { children: "Promotion" }), billingApproved === true ? (_jsx(Badge, { variant: "ok", text: "Eligible" })) : (_jsx(Badge, { variant: "off", text: "Not promoted" }))] }), _jsxs("div", { style: { display: 'flex', gap: '8px', marginTop: '16px', flexWrap: 'wrap' }, children: [_jsx("button", { type: "button", className: "btn p", onClick: () => setRoute('security'), children: "Open approval review" }), billingApproved === true && (_jsx("button", { type: "button", className: "btn p", style: { background: 'var(--ok)', borderColor: 'var(--ok)' }, onClick: handlePromote, children: "Promote to Registry \u2713" })), _jsx("button", { type: "button", className: "btn d", onClick: () => openModal('revoke', 'billing_api_client'), children: "Revoke\u2026" })] }), _jsx("p", { className: "help", children: "Jev never writes the code or makes the promotion decision." })] })] })] }));
};
