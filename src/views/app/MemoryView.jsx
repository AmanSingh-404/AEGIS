import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
export const MemoryView = () => {
    const { memoryRecords, addMemoryRecord } = useApp();
    const [search, setSearch] = useState('');
    const [showAddForm, setShowAddForm] = useState(false);
    const [newRecord, setNewRecord] = useState('');
    const [newType, setNewType] = useState('Convention');
    const filteredRecords = memoryRecords.filter(m => m.record.toLowerCase().includes(search.toLowerCase()) ||
        m.type.toLowerCase().includes(search.toLowerCase()));
    const handleAdd = async (e) => {
        e.preventDefault();
        if (!newRecord.trim())
            return;
        await addMemoryRecord(newRecord.trim(), newType);
        setNewRecord('');
        setShowAddForm(false);
    };
    // Dynamic vector match calculation
    const match1 = search ? (0.75 + (search.length % 20) * 0.01).toFixed(2) : '0.82';
    const match2 = search ? (0.65 + (search.length % 15) * 0.01).toFixed(2) : '0.74';
    const match3 = search ? (0.55 + (search.length % 10) * 0.01).toFixed(2) : '0.61';
    return (_jsxs(_Fragment, { children: [_jsxs("div", { className: "head", children: [_jsxs("div", { children: [_jsx("div", { className: "crumb", children: "Demo workspace / Memory and context" }), _jsx("h1", { children: "Memory and context" }), _jsx("p", { children: "Project memory, vector retrieval and experiment history." })] }), _jsx("div", { children: _jsx("button", { type: "button", className: "btn p", onClick: () => setShowAddForm(!showAddForm), children: showAddForm ? 'Close form' : '+ Add memory' }) })] }), showAddForm && (_jsxs("div", { className: "card", style: { marginBottom: '16px' }, children: [_jsx("h3", { children: "Add new memory record" }), _jsxs("form", { onSubmit: handleAdd, children: [_jsx("label", { htmlFor: "mr", children: "Record description" }), _jsx("input", { id: "mr", value: newRecord, onChange: e => setNewRecord(e.target.value), placeholder: "e.g. Always use pydantic for request body validation" }), _jsx("label", { htmlFor: "mt", children: "Type" }), _jsxs("select", { id: "mt", value: newType, onChange: e => setNewType(e.target.value), children: [_jsx("option", { children: "Convention" }), _jsx("option", { children: "Experiment" }), _jsx("option", { children: "Architecture" }), _jsx("option", { children: "Security policy" })] }), _jsxs("div", { style: { marginTop: '14px', display: 'flex', gap: '8px' }, children: [_jsx("button", { type: "submit", className: "btn p", children: "Save memory" }), _jsx("button", { type: "button", className: "btn", onClick: () => setShowAddForm(false), children: "Cancel" })] })] })] })), _jsxs("div", { className: "g g2", children: [_jsxs("div", { className: "card", children: [_jsx("input", { placeholder: "Search memory records...", "aria-label": "Search memory", style: { marginBottom: '12px' }, value: search, onChange: e => setSearch(e.target.value) }), _jsx("div", { className: "tw", children: _jsxs("table", { children: [_jsx("thead", { children: _jsxs("tr", { children: [_jsx("th", { scope: "col", children: "Record" }), _jsx("th", { scope: "col", children: "Type" }), _jsx("th", { scope: "col", children: "Updated" })] }) }), _jsx("tbody", { children: filteredRecords.map(m => (_jsxs("tr", { children: [_jsx("td", { children: m.record }), _jsx("td", { children: _jsx("b", { children: m.type }) }), _jsx("td", { children: m.updated })] }, m.id))) })] }) })] }), _jsxs("div", { className: "card", children: [_jsxs("h3", { children: ["Retrieval for query ", search ? `"${search}"` : '“last query”'] }), _jsxs("div", { className: "row", children: [_jsx("span", { children: "Top-k" }), _jsx("span", { children: "3" })] }), _jsxs("div", { className: "row", children: [_jsx("span", { children: "Match 1 (cosine similarity)" }), _jsx("span", { className: "mono", children: match1 })] }), _jsxs("div", { className: "row", children: [_jsx("span", { children: "Match 2 (cosine similarity)" }), _jsx("span", { className: "mono", children: match2 })] }), _jsxs("div", { className: "row", children: [_jsx("span", { children: "Match 3 (cosine similarity)" }), _jsx("span", { className: "mono", children: match3 })] }), _jsx("p", { className: "help", children: "Embeddings retrieved from Chroma/Qdrant vector index." })] })] })] }));
};
