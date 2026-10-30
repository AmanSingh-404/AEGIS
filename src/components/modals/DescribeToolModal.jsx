import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
export const DescribeToolModal = () => {
    const { closeModal, forgeNewCandidate } = useApp();
    const [desc, setDesc] = useState('');
    const handleCreate = async () => {
        if (!desc.trim())
            return;
        await forgeNewCandidate(desc.trim());
    };
    return (_jsx("div", { className: "modal-overlay", onClick: closeModal, children: _jsxs("div", { className: "modal-content", onClick: e => e.stopPropagation(), children: [_jsx("h3", { children: "Describe a new tool" }), _jsx("label", { htmlFor: "gd", children: "What should it do?" }), _jsx("textarea", { id: "gd", rows: 4, value: desc, onChange: e => setDesc(e.target.value), placeholder: "e.g. Fetch invoice data from internal billing service and convert currency" }), _jsx("div", { className: "help", style: { marginBottom: '14px' }, children: "Tool Forge drafts it, then it is sandbox-tested and validated before any review." }), _jsxs("div", { style: { display: 'flex', gap: '8px' }, children: [_jsx("button", { type: "button", className: "btn p", onClick: handleCreate, children: "Create draft" }), _jsx("button", { type: "button", className: "btn", onClick: closeModal, children: "Cancel" })] })] }) }));
};
