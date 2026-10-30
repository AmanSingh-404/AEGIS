import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import React, { useState, useRef, useEffect } from 'react';
import { useApp } from '../../context/AppContext';
export const TopHeader = () => {
    const { setRoute, showToast, openModal, pendingApprovalsCount, theme, toggleTheme } = useApp();
    const [notifOpen, setNotifOpen] = useState(false);
    const [profileOpen, setProfileOpen] = useState(false);
    const notifRef = useRef(null);
    const profileRef = useRef(null);
    useEffect(() => {
        const handleClickOutside = (e) => {
            if (notifRef.current && !notifRef.current.contains(e.target)) {
                setNotifOpen(false);
            }
            if (profileRef.current && !profileRef.current.contains(e.target)) {
                setProfileOpen(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);
    return (_jsxs("header", { className: "top", children: [_jsxs("div", { className: "ttl", children: ["AEGIS ", _jsx("span", { className: "plan", children: "App" })] }), _jsx("span", { className: "sp" }), _jsx("button", { type: "button", className: "pill", onClick: () => setRoute('landing'), title: "View the AEGIS Marketing & Solutions Landing Page", children: "\uD83C\uDF10 Landing Page" }), _jsx("span", { className: "demo", children: "Illustrative data" }), _jsx("button", { type: "button", className: "theme-toggle", onClick: toggleTheme, title: theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode', "aria-label": "Toggle theme", children: theme === 'dark' ? '☀️' : '🌙' }), _jsx("button", { type: "button", className: "pill", onClick: () => setRoute('settings'), children: "Configuration" }), _jsx("button", { type: "button", className: "pill", onClick: () => showToast('Share link copied to clipboard'), children: "Share" }), _jsxs("div", { style: { position: 'relative' }, ref: notifRef, children: [_jsxs("button", { type: "button", className: "ib", "aria-label": "Notifications", "aria-haspopup": "true", onClick: () => {
                            setNotifOpen(!notifOpen);
                            setProfileOpen(false);
                        }, children: ["\uD83D\uDD14", pendingApprovalsCount > 0 && (_jsx("span", { style: {
                                    position: 'absolute',
                                    top: '5px',
                                    right: '5px',
                                    width: '8px',
                                    height: '8px',
                                    borderRadius: '50%',
                                    background: 'var(--err)'
                                } }))] }), notifOpen && (_jsxs("div", { className: "menu", role: "menu", children: [_jsx("div", { children: _jsxs("b", { children: [pendingApprovalsCount, " approvals waiting"] }) }), _jsx("div", { style: { color: 'var(--mute)' }, children: "Tool Forge candidate passed sandbox" }), _jsx("button", { type: "button", onClick: () => {
                                    setNotifOpen(false);
                                    setRoute('security');
                                }, style: { color: 'var(--acc)', fontWeight: 500 }, children: "Open Security center \u2192" })] }))] }), _jsxs("div", { style: { position: 'relative' }, ref: profileRef, children: [_jsx("button", { type: "button", className: "ib", "aria-label": "Profile menu", "aria-haspopup": "true", onClick: () => {
                            setProfileOpen(!profileOpen);
                            setNotifOpen(false);
                        }, children: "YB" }), profileOpen && (_jsxs("div", { className: "menu", role: "menu", children: [_jsxs("div", { children: [_jsx("b", { children: "Yash Bansal" }), _jsx("br", {}), _jsx("span", { style: { color: 'var(--mute)' }, children: "yash@example.com" })] }), _jsx("button", { type: "button", onClick: () => {
                                    setProfileOpen(false);
                                    setRoute('settings');
                                }, children: "Account settings" }), _jsx("button", { type: "button", onClick: () => {
                                    setProfileOpen(false);
                                    setRoute('landing');
                                }, children: "Go to Landing Page" }), _jsx("button", { type: "button", onClick: () => {
                                    setProfileOpen(false);
                                    setRoute('signin');
                                }, children: "Sign out" })] }))] }), _jsx("button", { type: "button", className: "pill dk", onClick: () => openModal('newtask'), children: "New task \u2726" })] }));
};
