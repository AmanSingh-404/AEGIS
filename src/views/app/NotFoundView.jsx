import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import React from 'react';
import { useApp } from '../../context/AppContext';
export const NotFoundView = () => {
    const { setRoute } = useApp();
    return (_jsxs("div", { className: "nf", children: [_jsx("h1", { children: "404" }), _jsx("h2", { children: "This page isn't part of AEGIS." }), _jsx("p", { style: { color: 'var(--mute)', maxWidth: '44ch', margin: '12px 0 24px' }, children: "The address may be mistyped, or the page was removed. Go back to the dashboard or search for a task or tool." }), _jsxs("div", { style: { display: 'flex', gap: '10px' }, children: [_jsx("button", { type: "button", className: "btn p", onClick: () => setRoute('dash'), children: "Back to dashboard" }), _jsx("button", { type: "button", className: "btn", onClick: () => setRoute('tasks'), children: "View tasks" })] })] }));
};
