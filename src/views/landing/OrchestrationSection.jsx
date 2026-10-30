import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import React from 'react';
export const OrchestrationSection = () => {
    const steps = [
        { title: 'Task input', desc: 'An objective is submitted.' },
        { title: 'Planning', desc: 'Planner builds the step graph.' },
        { title: 'Decision', desc: 'Jev routes and pre-screens.' },
        { title: 'Agents', desc: 'Researcher, Coder, Analyst and others run.' },
        { title: 'Tools', desc: 'Registry tools run under policy.' },
        { title: 'Evaluation', desc: 'Critic judges; Repair retries.' },
        { title: 'Result', desc: 'Report with evidence and artifacts.' }
    ];
    return (_jsx("section", { id: "orchestration", style: { padding: '96px 0' }, children: _jsxs("div", { className: "wrap", children: [_jsx("div", { children: _jsx("h2", { style: { fontSize: 'clamp(34px, 5vw, 64px)', maxWidth: '16ch' }, children: "From intent to coordinated execution." }) }), _jsx("div", { className: "orch", children: steps.map((s, i) => (_jsxs("div", { children: [_jsx("i", {}), _jsx("b", { children: s.title }), _jsx("span", { children: s.desc })] }, i))) })] }) }));
};
