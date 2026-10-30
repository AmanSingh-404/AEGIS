import { jsxs as _jsxs, jsx as _jsx } from "react/jsx-runtime";
import React from 'react';
import { useApp } from '../../context/AppContext';
export const RevokeModal = () => {
    const { closeModal, confirmRevoke, targetRevokeTool } = useApp();
    return (_jsx("div", { className: "modal-overlay", onClick: closeModal, children: _jsxs("div", { className: "modal-content", onClick: e => e.stopPropagation(), children: [_jsxs("h3", { children: ["Revoke ", targetRevokeTool ? `“${targetRevokeTool}”` : 'this tool', "?"] }), _jsx("p", { style: { color: 'var(--mute)', margin: '10px 0 20px' }, children: "It will be removed from what the Planner can select and blocked by the Policy Engine platform-wide. This is logged." }), _jsxs("div", { style: { display: 'flex', gap: '8px' }, children: [_jsx("button", { type: "button", className: "btn d", onClick: confirmRevoke, children: "Revoke tool" }), _jsx("button", { type: "button", className: "btn", onClick: closeModal, children: "Cancel" })] })] }) }));
};
