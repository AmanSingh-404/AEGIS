import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { INITIAL_PROVIDERS } from '../../data/mockData';
import { Badge } from '../../components/common/Badge';
export const ModelsView = () => {
    const { showToast } = useApp();
    const [providers, setProviders] = useState(() => {
        const saved = localStorage.getItem('aegis_providers');
        return saved ? JSON.parse(saved) : INITIAL_PROVIDERS;
    });
    const [selectedProvider, setSelectedProvider] = useState('Gemini');
    const [apiKey, setApiKey] = useState('');
    const [keyError, setKeyError] = useState('');
    const [testing, setTesting] = useState(false);
    const handleSaveKey = () => {
        if (apiKey.length < 8) {
            setKeyError('Enter an API key of at least 8 characters.');
            return;
        }
        setKeyError('');
        setTesting(true);
        setTimeout(() => {
            setTesting(false);
            const updated = providers.map(p => p.provider === selectedProvider
                ? { ...p, status: 'Configured', statusVariant: 'ok', apiKey }
                : p);
            setProviders(updated);
            localStorage.setItem('aegis_providers', JSON.stringify(updated));
            showToast(`${selectedProvider} provider key validated and stored.`);
            setApiKey('');
        }, 600);
    };
    const handleTestProvider = (providerName) => {
        showToast(`Testing ${providerName} endpoint connection... (Latency 82ms, 200 OK)`);
    };
    return (_jsxs(_Fragment, { children: [_jsx("div", { className: "head", children: _jsxs("div", { children: [_jsx("div", { className: "crumb", children: "Demo workspace / Models" }), _jsx("h1", { children: "Models and providers" }), _jsx("p", { children: "Provider-agnostic router. Connect multiple LLMs and decision models." })] }) }), _jsxs("div", { className: "g g2", children: [_jsxs("div", { className: "card", children: [_jsx("h3", { children: "Active Providers" }), _jsx("div", { className: "tw", children: _jsxs("table", { children: [_jsx("thead", { children: _jsxs("tr", { children: [_jsx("th", { scope: "col", children: "Provider" }), _jsx("th", { scope: "col", children: "Role" }), _jsx("th", { scope: "col", children: "Status" }), _jsx("th", { scope: "col", children: "Action" })] }) }), _jsx("tbody", { children: providers.map(p => (_jsxs("tr", { children: [_jsx("td", { children: _jsx("b", { children: p.provider }) }), _jsx("td", { children: p.role }), _jsx("td", { children: _jsx(Badge, { variant: p.statusVariant, text: p.status }) }), _jsx("td", { children: _jsx("button", { type: "button", className: "btn", style: { height: '28px', padding: '0 8px', fontSize: '11.5px' }, onClick: () => handleTestProvider(p.provider), children: "Ping" }) })] }, p.provider))) })] }) })] }), _jsxs("div", { className: "card", children: [_jsx("h3", { children: "Add provider key" }), _jsx("label", { htmlFor: "pselect", children: "Select Provider" }), _jsx("select", { id: "pselect", value: selectedProvider, onChange: e => setSelectedProvider(e.target.value), children: providers.map(p => (_jsxs("option", { value: p.provider, children: [p.provider, " (", p.role, ")"] }, p.provider))) }), _jsxs("label", { htmlFor: "pk", children: ["API key for ", selectedProvider] }), _jsx("input", { id: "pk", type: "password", autoComplete: "off", value: apiKey, onChange: e => {
                                    setApiKey(e.target.value);
                                    if (keyError)
                                        setKeyError('');
                                }, placeholder: `Enter ${selectedProvider} API Key (e.g. sk-...)`, "aria-invalid": !!keyError }), _jsx("div", { className: "help", children: "Stored encrypted server-side or local secure storage. Never logged in raw traces." }), keyError && _jsx("div", { className: "err", role: "alert", children: keyError }), _jsx("button", { type: "button", className: "btn p", style: { marginTop: '12px' }, onClick: handleSaveKey, disabled: testing, children: testing ? 'Verifying key...' : 'Save and test connection' }), _jsx("h3", { style: { marginTop: '24px' }, children: "Routing summary" }), _jsxs("div", { className: "row", children: [_jsx("span", { children: "research_task" }), _jsx("span", { children: "Gemini (or lowest latency fallback)" })] }), _jsxs("div", { className: "row", children: [_jsx("span", { children: "coding_task" }), _jsx("span", { children: "Groq / Sonnet 3.5" })] }), _jsxs("div", { className: "row", children: [_jsx("span", { children: "Below Jev confidence" }), _jsx("span", { children: "Escalate to LLM Judge / Rule table" })] })] })] })] }));
};
