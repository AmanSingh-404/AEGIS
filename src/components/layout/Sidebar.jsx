import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import React from 'react';
import { useApp } from '../../context/AppContext';
import { Logo } from '../common/Logo';
import { GlobeIcon, HomeIcon, DashIcon, TasksIcon, AgentsIcon, JevIcon, ForgeIcon, ToolsIcon, MemoryIcon, EvalIcon, SecurityIcon, ModelsIcon, SettingsIcon, StatesIcon, SignOutIcon } from '../common/Icons';
export const Sidebar = () => {
    const { currentRoute, setRoute, pendingApprovalsCount } = useApp();
    const navItems = [
        { key: 'home', label: 'Home', icon: _jsx(HomeIcon, {}) },
        { key: 'dash', label: 'Dashboard', icon: _jsx(DashIcon, {}) },
        { key: 'tasks', label: 'Tasks', icon: _jsx(TasksIcon, {}) },
        { key: 'agents', label: 'Agents', icon: _jsx(AgentsIcon, {}) },
        { key: 'jev', label: 'Jev decisions', icon: _jsx(JevIcon, {}) },
        { key: 'forge', label: 'Tool Forge', icon: _jsx(ForgeIcon, {}) },
        { key: 'tools', label: 'Tools library', icon: _jsx(ToolsIcon, {}) },
        { key: 'memory', label: 'Memory', icon: _jsx(MemoryIcon, {}) },
        { key: 'eval', label: 'Evaluation lab', icon: _jsx(EvalIcon, {}) },
        { key: 'security', label: 'Security center', icon: _jsx(SecurityIcon, {}) },
        { key: 'models', label: 'Models', icon: _jsx(ModelsIcon, {}) },
        { key: 'settings', label: 'Settings', icon: _jsx(SettingsIcon, {}) },
        { key: 'states', label: 'UI states', icon: _jsx(StatesIcon, {}) }
    ];
    return (_jsxs("nav", { className: "side", "aria-label": "Main", children: [_jsx("div", { className: "logo", onClick: () => setRoute('landing'), title: "AEGIS Landing Page", children: _jsx(Logo, { size: 30 }) }), _jsx("button", { type: "button", className: "nav-btn", onClick: () => setRoute('landing'), title: "Website / Landing Page", "aria-label": "Website / Landing Page", children: _jsx(GlobeIcon, {}) }), navItems.map(item => {
                const isActive = currentRoute === item.key;
                return (_jsxs("button", { type: "button", className: `nav-btn ${isActive ? 'active' : ''}`, onClick: () => setRoute(item.key), title: item.label, "aria-label": item.label, "aria-current": isActive ? 'page' : undefined, children: [item.icon, item.key === 'security' && pendingApprovalsCount > 0 && _jsx("i", { className: "dot" })] }, item.key));
            }), _jsx("span", { className: "sp" }), _jsx("button", { type: "button", className: "nav-btn", onClick: () => setRoute('signin'), title: "Sign out", "aria-label": "Sign out", children: _jsx(SignOutIcon, {}) })] }));
};
