import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { Badge } from '../../components/common/Badge';
import { DOMAIN_PLAN_MAP } from '../../data/mockData';
export const HomeView = () => {
    const { setRoute, pendingApprovalsCount, addNewTask } = useApp();
    const [objective, setObjective] = useState('');
    const [selectedDomain, setSelectedDomain] = useState('Software Engineering');
    const [error, setError] = useState('');
    const [showPlan, setShowPlan] = useState(false);
    const [submittedObjective, setSubmittedObjective] = useState('');
    const [isExecuting, setIsExecuting] = useState(false);
    const domains = [
        'Software Engineering',
        'Research',
        'Data Analysis',
        'AI/ML Engineering',
        'AI Security'
    ];
    const handlePreviewPlan = () => {
        if (!objective.trim()) {
            setError('Describe an objective first.');
            setShowPlan(false);
            return;
        }
        setError('');
        setSubmittedObjective(objective.trim());
        setShowPlan(true);
    };
    const handleRunTask = async () => {
        if (!objective.trim()) {
            setError('Describe an objective first.');
            return;
        }
        setIsExecuting(true);
        await addNewTask(objective.trim(), selectedDomain);
        setIsExecuting(false);
        setRoute('tasks');
    };
    const domainDetails = DOMAIN_PLAN_MAP[selectedDomain] || DOMAIN_PLAN_MAP['Software Engineering'];
    return (_jsxs("div", { className: "hm", children: [_jsx("div", { className: "orb", "aria-hidden": "true" }), _jsx("h2", { className: "hi", children: "What should your AI workforce do?" }), _jsx("p", { className: "sub", children: "AEGIS plans the work, picks agents and tools, and pauses for approval before anything risky runs." }), _jsxs("div", { className: "cmp", children: [_jsx("label", { htmlFor: "obj", style: { position: 'absolute', left: '-9999px' }, children: "Objective" }), _jsx("input", { id: "obj", placeholder: "e.g. Find why the API tests fail and prepare a fix", value: objective, onChange: e => {
                            setObjective(e.target.value);
                            if (error)
                                setError('');
                        }, onKeyDown: e => {
                            if (e.key === 'Enter')
                                handlePreviewPlan();
                        }, "aria-invalid": !!error }), _jsx("div", { className: "dm", role: "group", "aria-label": "Domain", children: domains.map(d => (_jsx("button", { type: "button", "data-dom": d, "aria-pressed": selectedDomain === d, onClick: () => setSelectedDomain(d), children: d }, d))) }), error && _jsx("div", { className: "err", role: "alert", children: error }), _jsxs("div", { className: "cb", children: [_jsx("span", { className: "help", children: "Simulated preview or launch live agent pipeline." }), _jsxs("div", { style: { display: 'flex', gap: '8px' }, children: [_jsx("button", { type: "button", className: "btn", style: { height: '34px', fontSize: '13px' }, onClick: handlePreviewPlan, children: "Preview plan" }), _jsx("button", { type: "button", className: "run", onClick: handleRunTask, disabled: isExecuting, children: isExecuting ? 'Planning...' : 'Run task' })] })] })] }), showPlan && (_jsxs("div", { className: "pv", children: [_jsxs("h3", { children: ["Plan preview ", _jsx(Badge, { variant: "wait", text: "Simulated" })] }), _jsx("p", { style: { margin: '0 0 12px', color: 'var(--mute)' }, children: submittedObjective }), _jsxs("ul", { className: "trace", children: [_jsxs("li", { className: "ok", children: [_jsx("b", { children: "Planner" }), " builds dependency-aware steps"] }), _jsxs("li", { className: "ok", children: [_jsx("b", { children: "Jev (Choice)" }), " suggests a model", _jsx("em", { children: "Advisory, with confidence. Below threshold it escalates." })] }), _jsxs("li", { className: "ok", children: [_jsx("b", { children: domainDetails[0] }), " runs the steps", _jsxs("em", { children: ["Tools: ", domainDetails[1]] })] }), _jsxs("li", { className: "wt", children: [_jsx("b", { children: "Policy Engine" }), " decides each tool call", _jsx("em", { children: domainDetails[2] })] }), _jsxs("li", { children: [_jsx("b", { children: "Critic" }), " evaluates; Repair retries up to 3 times"] }), _jsxs("li", { children: [_jsx("b", { children: "Report" }), " returns evidence and artifacts", _jsx("em", { children: "If no tool fits, a capability gap goes to Tool Forge. A forged tool is sandbox-tested, validated and policy-checked, with human review when required, before promotion." })] })] }), _jsx("div", { style: { marginTop: '16px', display: 'flex', gap: '8px' }, children: _jsx("button", { type: "button", className: "btn p", onClick: handleRunTask, disabled: isExecuting, children: "Execute this plan now \u2192" }) })] })), _jsxs("div", { className: "hc", children: [_jsxs("div", { className: "c dk", children: [_jsxs("div", { className: "ch", children: [_jsx("span", { children: "Needs your approval" }), _jsxs("span", { className: "bd", children: [pendingApprovalsCount, " pending"] })] }), _jsxs("ul", { children: [_jsx("li", { children: "billing_api_client: first live call" }), _jsx("li", { children: "github: open pull request" })] }), _jsxs("div", { className: "cf", style: { background: 'rgba(255,255,255,.08)', color: '#cfd3e6' }, children: [_jsx("span", { children: "Policy Engine" }), _jsx("button", { type: "button", onClick: () => setRoute('security'), style: { color: '#fff' }, children: "Review" })] })] }), _jsxs("div", { className: "c", children: [_jsxs("ul", { children: [_jsx("li", { children: _jsx(Badge, { variant: "wait", text: "Candidate in review" }) }), _jsx("li", { children: _jsx(Badge, { variant: "run", text: "2 open capability gaps" }) }), _jsx("li", { children: _jsx(Badge, { variant: "ok", text: "fx_rate_fetch v2 promoted" }) })] }), _jsxs("div", { className: "cf", children: [_jsx("span", { children: "Tool Forge" }), _jsx("button", { type: "button", onClick: () => setRoute('forge'), children: "Open" })] })] }), _jsxs("div", { className: "c", children: [_jsxs("p", { style: { paddingBottom: 0 }, children: [_jsx("b", { children: "Jev cascade (demo)" }), _jsx("br", {}), _jsx("span", { style: { color: 'var(--mute)' }, children: "82% resolved by Jev, 18% escalated to LLM or human." })] }), _jsx("div", { className: "bar", role: "img", "aria-label": "82 percent resolved by Jev", style: { margin: '6px 14px 0' }, children: _jsx("i", { style: { width: '82%' } }) }), _jsx("p", { className: "help", style: { padding: '6px 14px' }, children: "Advisory only." }), _jsxs("div", { className: "cf", children: [_jsx("span", { children: "Decisions" }), _jsx("button", { type: "button", onClick: () => setRoute('jev'), children: "Open" })] })] })] }), _jsx("p", { className: "fn", children: "AEGIS shows transparent action summaries, logs, and verifiable execution evidence." })] }));
};
