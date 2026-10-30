import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { Badge } from '../../components/common/Badge';
import { api } from '../../services/api';
export const ToolsView = () => {
    const { tools, openModal, showToast } = useApp();
    const [search, setSearch] = useState('');
    const [originFilter, setOriginFilter] = useState('All');
    const [riskFilter, setRiskFilter] = useState('All');
    const filteredTools = tools.filter(t => {
        const matchesSearch = t.name.toLowerCase().includes(search.toLowerCase()) ||
            t.version.toLowerCase().includes(search.toLowerCase());
        const matchesOrigin = originFilter === 'All' || t.origin === originFilter;
        const matchesRisk = riskFilter === 'All' || t.risk === riskFilter;
        return matchesSearch && matchesOrigin && matchesRisk;
    });
    const handleTestTool = (name) => {
        showToast(`Dry-run sandbox test passed for "${name}" (0 errors)`);
    };
    const handleReenable = async (name) => {
        await api.enableTool(name);
        window.location.reload();
    };
    return (_jsxs(_Fragment, { children: [_jsx("div", { className: "head", children: _jsxs("div", { children: [_jsx("div", { className: "crumb", children: "Demo workspace / Tools library" }), _jsx("h1", { children: "Tools library" }), _jsx("p", { children: "Registered and forged tools with runtime governance." })] }) }), _jsxs("div", { className: "card", children: [_jsxs("div", { style: { display: 'flex', gap: '8px', marginBottom: '12px', flexWrap: 'wrap' }, children: [_jsx("input", { placeholder: "Search tools", "aria-label": "Search tools", style: { flex: 1, minWidth: '160px' }, value: search, onChange: e => setSearch(e.target.value) }), _jsxs("select", { "aria-label": "Filter origin", style: { width: 'auto' }, value: originFilter, onChange: e => setOriginFilter(e.target.value), children: [_jsx("option", { value: "All", children: "All origins" }), _jsx("option", { value: "registered", children: "registered" }), _jsx("option", { value: "forged", children: "forged" })] }), _jsxs("select", { "aria-label": "Filter risk", style: { width: 'auto' }, value: riskFilter, onChange: e => setRiskFilter(e.target.value), children: [_jsx("option", { value: "All", children: "All risks" }), _jsx("option", { value: "Low", children: "Low risk" }), _jsx("option", { value: "Medium", children: "Medium risk" }), _jsx("option", { value: "High", children: "High risk" })] })] }), _jsx("div", { className: "tw", children: _jsxs("table", { children: [_jsx("thead", { children: _jsxs("tr", { children: [_jsx("th", { scope: "col", children: "Tool" }), _jsx("th", { scope: "col", children: "Origin" }), _jsx("th", { scope: "col", children: "Version" }), _jsx("th", { scope: "col", children: "Risk" }), _jsx("th", { scope: "col", children: "Validation" }), _jsx("th", { scope: "col", children: "Actions" })] }) }), _jsx("tbody", { children: filteredTools.map(t => (_jsxs("tr", { children: [_jsx("td", { children: _jsx("span", { className: "mono", children: t.name }) }), _jsx("td", { children: t.origin }), _jsx("td", { children: _jsx("span", { className: "mono", children: t.version }) }), _jsx("td", { children: t.risk }), _jsx("td", { children: _jsx(Badge, { variant: t.validationVariant, text: t.validation }) }), _jsx("td", { children: _jsxs("div", { style: { display: 'flex', gap: '6px' }, children: [_jsx("button", { type: "button", className: "btn", style: { height: '28px', padding: '0 8px', fontSize: '11.5px' }, onClick: () => handleTestTool(t.name), children: "Test" }), !t.revoked && t.validationVariant !== 'bad' ? (_jsx("button", { type: "button", className: "btn d", style: { height: '28px', padding: '0 8px', fontSize: '11.5px' }, onClick: () => openModal('revoke', t.name), children: "Revoke" })) : t.revoked ? (_jsx("button", { type: "button", className: "btn p", style: { height: '28px', padding: '0 8px', fontSize: '11.5px' }, onClick: () => handleReenable(t.name), children: "Enable" })) : null] }) })] }, t.name))) })] }) })] })] }));
};
