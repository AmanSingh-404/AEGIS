import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
export const NewTaskModal = () => {
    const { closeModal, addNewTask } = useApp();
    const [objective, setObjective] = useState('');
    const [domain, setDomain] = useState('Software Engineering');
    const [maxRetries, setMaxRetries] = useState(3);
    const [budget, setBudget] = useState(2);
    const [error, setError] = useState('');
    const handleSubmit = (e) => {
        e.preventDefault();
        if (!objective.trim()) {
            setError('Describe an objective to create a task.');
            return;
        }
        addNewTask(objective.trim(), domain);
    };
    return (_jsx("div", { className: "modal-overlay", onClick: closeModal, children: _jsxs("div", { className: "modal-content", onClick: e => e.stopPropagation(), children: [_jsxs("div", { className: "dh", children: [_jsx("h3", { children: "New task" }), _jsx("button", { type: "button", className: "btn x", onClick: closeModal, "aria-label": "Close", children: "\u2715" })] }), _jsx("p", { className: "help", style: { margin: 0 }, children: "Describe the outcome you want. AEGIS plans the steps, and you stay in control of risky actions." }), _jsxs("form", { onSubmit: handleSubmit, children: [_jsx("label", { htmlFor: "nt", children: "Objective" }), _jsx("textarea", { id: "nt", rows: 4, placeholder: "e.g. Find why the API tests fail and prepare a fix", value: objective, onChange: e => {
                                setObjective(e.target.value);
                                if (error)
                                    setError('');
                            }, "aria-invalid": !!error }), error && _jsx("div", { className: "err", role: "alert", children: error }), _jsx("label", { htmlFor: "nd", children: "Domain" }), _jsxs("select", { id: "nd", value: domain, onChange: e => setDomain(e.target.value), children: [_jsx("option", { children: "Software Engineering" }), _jsx("option", { children: "Research" }), _jsx("option", { children: "Data Analysis" }), _jsx("option", { children: "AI/ML Engineering" }), _jsx("option", { children: "AI Security" })] }), _jsxs("div", { className: "two", children: [_jsxs("div", { children: [_jsx("label", { htmlFor: "nr", children: "Max retries" }), _jsx("input", { id: "nr", type: "number", min: "0", max: "3", value: maxRetries, onChange: e => setMaxRetries(Number(e.target.value)) })] }), _jsxs("div", { children: [_jsx("label", { htmlFor: "nb", children: "Budget cap (demo, USD)" }), _jsx("input", { id: "nb", type: "number", min: "1", value: budget, onChange: e => setBudget(Number(e.target.value)) })] })] }), _jsx("div", { className: "pn", children: "High-risk actions always pause for approval. Prototype: no agent runs." }), _jsxs("div", { style: { display: 'flex', gap: '8px', marginTop: '18px' }, children: [_jsx("button", { type: "submit", className: "btn p", children: "Create task" }), _jsx("button", { type: "button", className: "btn", onClick: closeModal, children: "Cancel" })] })] })] }) }));
};
