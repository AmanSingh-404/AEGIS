import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import React from 'react';
import { INITIAL_AGENTS } from '../../data/mockData';
import { Badge } from '../../components/common/Badge';
export const AgentsView = () => {
    return (_jsxs(_Fragment, { children: [_jsx("div", { className: "head", children: _jsxs("div", { children: [_jsx("div", { className: "crumb", children: "Demo workspace / Agents" }), _jsx("h1", { children: "Agents" }), _jsx("p", { children: "Agent catalog and tool access." })] }) }), _jsx("div", { className: "g g3", children: INITIAL_AGENTS.map(agent => (_jsxs("div", { className: "card", children: [_jsx("h3", { children: agent.name }), _jsx("p", { style: { color: 'var(--mute)', margin: '0 0 10px' }, children: agent.description }), _jsxs("div", { className: "row", children: [_jsx("span", { children: "Tool access" }), _jsx("span", { className: "mono", children: agent.tools })] }), _jsxs("div", { className: "row", children: [_jsx("span", { children: "Status" }), _jsx(Badge, { variant: agent.statusVariant, text: agent.status })] })] }, agent.name))) })] }));
};
