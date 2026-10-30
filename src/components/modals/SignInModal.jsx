import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
export const SignInModal = () => {
    const { closeModal, showToast, setRoute } = useApp();
    const [email, setEmail] = useState('');
    const [error, setError] = useState('');
    const handleSignIn = (e) => {
        e.preventDefault();
        if (!email.trim() || !/^\S+@\S+\.\S+$/.test(email)) {
            setError('Enter an email address like name@example.com.');
            return;
        }
        closeModal();
        showToast('Signed in as demo user');
        setRoute('home');
    };
    return (_jsx("div", { className: "modal-overlay", onClick: closeModal, children: _jsxs("div", { className: "modal-content", onClick: e => e.stopPropagation(), children: [_jsxs("div", { className: "dh", children: [_jsx("h3", { children: "Sign in to AEGIS" }), _jsx("button", { type: "button", className: "btn x", onClick: closeModal, "aria-label": "Close", children: "\u2715" })] }), _jsx("p", { className: "help", style: { margin: '0 0 16px' }, children: "Visual prototype. Enter any email to continue to workspace." }), _jsxs("form", { onSubmit: handleSignIn, children: [_jsx("label", { htmlFor: "em", style: { fontSize: '14px', fontWeight: 500 }, children: "Email" }), _jsx("input", { id: "em", type: "email", value: email, onChange: e => {
                                setEmail(e.target.value);
                                if (error)
                                    setError('');
                            }, placeholder: "name@example.com", style: { display: 'block', width: '100%', height: '44px', margin: '6px 0 4px', padding: '0 14px', border: '1px solid var(--line)', borderRadius: '10px' }, "aria-invalid": !!error }), error && _jsx("p", { className: "err", style: { minHeight: '20px', margin: 0 }, role: "alert", children: error }), _jsxs("div", { style: { display: 'flex', gap: '10px', marginTop: '16px' }, children: [_jsx("button", { type: "submit", className: "btn p", children: "Continue" }), _jsx("button", { type: "button", className: "btn", onClick: closeModal, children: "Close" })] })] })] }) }));
};
