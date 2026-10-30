import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import React from 'react';
import { useApp } from '../../context/AppContext';
export const DomainsSection = () => {
    const { setRoute } = useApp();
    const domains = [
        {
            name: 'Software Engineering',
            desc: 'Repository understanding, coding, debugging, testing, PR preparation.'
        },
        {
            name: 'Research',
            desc: 'Web research, evidence extraction, citation-aware reports.'
        },
        {
            name: 'Data Analysis',
            desc: 'CSV and JSON analysis with sandboxed Python.'
        },
        {
            name: 'AI/ML Engineering',
            desc: 'RAG construction, retrieval experiments, evaluation.'
        },
        {
            name: 'AI Security',
            desc: 'Prompt-injection, tool-abuse and data-leakage checks.'
        }
    ];
    return (_jsx("section", { id: "domains", style: { padding: '96px 0' }, children: _jsxs("div", { className: "wrap", children: [_jsxs("div", { children: [_jsx("h2", { style: { fontSize: 'clamp(34px, 5vw, 64px)', maxWidth: '16ch' }, children: "Five domains for the MVP." }), _jsx("p", { className: "lead", children: "DevOps, Database/API, Automation and Project/Product Work are out of MVP scope." })] }), _jsx("div", { className: "dom", style: { marginTop: '48px' }, children: domains.map(d => (_jsxs("div", { onClick: () => setRoute('home'), style: {
                            cursor: 'pointer',
                            display: 'grid',
                            gridTemplateColumns: 'minmax(200px, 1fr) 2fr',
                            gap: '24px',
                            padding: '26px 0',
                            borderBottom: '1px solid var(--line)',
                            transition: 'padding 0.3s, background 0.3s'
                        }, children: [_jsx("b", { children: d.name }), _jsx("span", { children: d.desc })] }, d.name))) })] }) }));
};
