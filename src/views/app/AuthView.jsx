import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import React, { useState, useEffect } from 'react';
import { useApp } from '../../context/AppContext';
import { Logo } from '../../components/common/Logo';
export const AuthView = ({ mode }) => {
    const { setRoute, showToast } = useApp();
    const [activeMode, setActiveMode] = useState(mode);
    // Form states - Yash Bansal
    const [fullName, setFullName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [rememberMe, setRememberMe] = useState(false);
    // Password visibility
    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);
    // Errors & Loading & Done
    const [errors, setErrors] = useState({});
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [isDone, setIsDone] = useState(false);
    useEffect(() => {
        setActiveMode(mode);
        setErrors({});
        setIsDone(false);
    }, [mode]);
    // Password strength calculation
    const calculateStrength = (p) => {
        let s = 0;
        if (p.length >= 8)
            s++;
        if (/[a-z]/.test(p) && /[A-Z]/.test(p))
            s++;
        if (/\d/.test(p))
            s++;
        if (/[^A-Za-z0-9]/.test(p))
            s++;
        return s;
    };
    const strength = calculateStrength(password);
    const strengthLabels = ['Weak', 'Weak', 'Fair', 'Good', 'Strong'];
    const handleSubmit = (e) => {
        e.preventDefault();
        const newErrors = {};
        if (activeMode === 'signup' && fullName.trim().length <= 1) {
            newErrors.fullName = 'Enter your full name.';
        }
        if (!email.trim() || !/^\S+@\S+\.\S+$/.test(email)) {
            newErrors.email = 'Enter an email like name@example.com.';
        }
        if (activeMode !== 'forgot') {
            if (activeMode === 'signin') {
                if (!password) {
                    newErrors.password = 'Enter your password.';
                }
            }
            else {
                if (password.length < 8 || strength < 3) {
                    newErrors.password = 'Use 8+ characters with letters, a number and a symbol.';
                }
                if (confirmPassword !== password) {
                    newErrors.confirmPassword = 'Passwords do not match.';
                }
            }
        }
        if (Object.keys(newErrors).length > 0) {
            setErrors(newErrors);
            return;
        }
        setErrors({});
        setIsSubmitting(true);
        setTimeout(() => {
            setIsSubmitting(false);
            setIsDone(true);
            showToast(activeMode === 'signin'
                ? 'Signed in successfully (demo)'
                : activeMode === 'signup'
                    ? 'Account created successfully (demo)'
                    : 'Password reset link sent (demo)');
        }, 600);
    };
    const doneMessages = {
        signin: [
            'Signed in (demo)',
            'Welcome back, Yash Bansal! Opening your workspace.'
        ],
        signup: [
            'Account created (demo)',
            'Welcome to AEGIS, Yash Bansal! Your workspace is ready.'
        ],
        forgot: [
            'Check your email (demo)',
            'Password reset instructions have been dispatched.'
        ]
    };
    return (_jsxs("div", { className: "auth-wrap", children: [_jsxs("div", { className: "l", children: [_jsxs("div", { className: "logo", onClick: () => setRoute('landing'), title: "Return to AEGIS Landing Page", children: [_jsx(Logo, { size: 30 }), _jsx("span", { children: "AEGIS" })] }), _jsx("main", { className: "box", "aria-live": "polite", children: isDone ? (_jsxs("div", { className: "view done", children: [_jsx("div", { className: "tick", "aria-hidden": "true", children: "\u2713" }), _jsx("h1", { style: { fontSize: '28px' }, children: doneMessages[activeMode][0] }), _jsx("p", { className: "sub", style: { marginTop: '10px' }, children: doneMessages[activeMode][1] }), _jsxs("div", { style: { display: 'flex', gap: '10px', marginTop: '20px' }, children: [_jsx("button", { type: "button", className: "btn p", onClick: () => setRoute('home'), children: "Enter Workspace \u2192" }), _jsx("button", { type: "button", className: "btn", onClick: () => {
                                                setIsDone(false);
                                                setRoute('signin');
                                            }, children: "Back to sign in" })] })] })) : (_jsxs("div", { className: "view", children: [activeMode !== 'forgot' && (_jsxs("nav", { className: "seg", "aria-label": "Authentication", children: [_jsx("button", { type: "button", className: activeMode === 'signin' ? 'active' : '', onClick: () => {
                                                setActiveMode('signin');
                                                setRoute('signin');
                                            }, children: "Sign in" }), _jsx("button", { type: "button", className: activeMode === 'signup' ? 'active' : '', onClick: () => {
                                                setActiveMode('signup');
                                                setRoute('signup');
                                            }, children: "Create account" })] })), activeMode === 'signin' && (_jsxs(_Fragment, { children: [_jsx("h1", { children: "Welcome back" }), _jsx("p", { className: "sub", children: "Sign in to your AEGIS workspace." })] })), activeMode === 'signup' && (_jsxs(_Fragment, { children: [_jsx("h1", { children: "Create your account" }), _jsx("p", { className: "sub", children: "Set up access to an AEGIS workspace." })] })), activeMode === 'forgot' && (_jsxs(_Fragment, { children: [_jsx("h1", { children: "Reset your password" }), _jsx("p", { className: "sub", children: "Enter your account email. Prototype: no message is sent." })] })), _jsxs("form", { onSubmit: handleSubmit, noValidate: true, children: [activeMode === 'signup' && (_jsxs("div", { children: [_jsx("label", { htmlFor: "nm", children: "Full name" }), _jsx("div", { className: "f", children: _jsx("input", { id: "nm", type: "text", autoComplete: "name", value: fullName, onChange: e => {
                                                            setFullName(e.target.value);
                                                            if (errors.fullName)
                                                                setErrors(prev => ({ ...prev, fullName: '' }));
                                                        }, placeholder: "Yash Bansal", "aria-invalid": !!errors.fullName }) }), errors.fullName && _jsx("div", { className: "err", role: "alert", children: errors.fullName })] })), _jsxs("div", { children: [_jsx("label", { htmlFor: "em", children: "Email" }), _jsx("div", { className: "f", children: _jsx("input", { id: "em", type: "email", autoComplete: "email", value: email, onChange: e => {
                                                            setEmail(e.target.value);
                                                            if (errors.email)
                                                                setErrors(prev => ({ ...prev, email: '' }));
                                                        }, placeholder: "yash@example.com", "aria-invalid": !!errors.email }) }), errors.email && _jsx("div", { className: "err", role: "alert", children: errors.email })] }), activeMode !== 'forgot' && (_jsxs("div", { children: [_jsx("label", { htmlFor: "pw", children: "Password" }), _jsxs("div", { className: "f", children: [_jsx("input", { id: "pw", type: showPassword ? 'text' : 'password', autoComplete: activeMode === 'signin' ? 'current-password' : 'new-password', value: password, onChange: e => {
                                                                setPassword(e.target.value);
                                                                if (errors.password)
                                                                    setErrors(prev => ({ ...prev, password: '' }));
                                                            }, placeholder: "\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022", "aria-invalid": !!errors.password }), _jsx("button", { type: "button", className: "eye", onClick: () => setShowPassword(!showPassword), "aria-pressed": showPassword, "aria-label": showPassword ? 'Hide password' : 'Show password', children: showPassword ? 'Hide' : 'Show' })] }), errors.password && _jsx("div", { className: "err", role: "alert", children: errors.password }), activeMode === 'signup' && (_jsxs(_Fragment, { children: [_jsxs("div", { className: "meter", "aria-hidden": "true", children: [_jsx("i", { className: strength >= 1 ? 'on' : '' }), _jsx("i", { className: strength >= 2 ? 'on' : '' }), _jsx("i", { className: strength >= 3 ? 'on' : '' }), _jsx("i", { className: strength >= 4 ? 'on' : '' })] }), _jsx("div", { className: "help", style: { marginTop: '6px' }, children: password ? `${strengthLabels[strength]} password` : 'Use 8+ characters with letters, a number and a symbol.' })] }))] })), activeMode === 'signup' && (_jsxs("div", { children: [_jsx("label", { htmlFor: "pc", children: "Confirm password" }), _jsxs("div", { className: "f", children: [_jsx("input", { id: "pc", type: showConfirmPassword ? 'text' : 'password', autoComplete: "new-password", value: confirmPassword, onChange: e => {
                                                                setConfirmPassword(e.target.value);
                                                                if (errors.confirmPassword)
                                                                    setErrors(prev => ({ ...prev, confirmPassword: '' }));
                                                            }, placeholder: "\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022", "aria-invalid": !!errors.confirmPassword }), _jsx("button", { type: "button", className: "eye", onClick: () => setShowConfirmPassword(!showConfirmPassword), "aria-pressed": showConfirmPassword, "aria-label": showConfirmPassword ? 'Hide password' : 'Show password', children: showConfirmPassword ? 'Hide' : 'Show' })] }), errors.confirmPassword && _jsx("div", { className: "err", role: "alert", children: errors.confirmPassword })] })), activeMode === 'signin' && (_jsxs("div", { className: "row", children: [_jsxs("label", { className: "chk", children: [_jsx("input", { type: "checkbox", checked: rememberMe, onChange: e => setRememberMe(e.target.checked) }), _jsx("span", { children: "Remember me" })] }), _jsx("button", { type: "button", onClick: () => {
                                                        setActiveMode('forgot');
                                                        setRoute('forgot');
                                                    }, style: { color: 'var(--acc)', border: 0, background: 'none', cursor: 'pointer', padding: 0 }, children: "Forgot password?" })] })), _jsx("button", { type: "submit", className: "btn", disabled: isSubmitting, style: {
                                                width: '100%',
                                                height: '48px',
                                                marginTop: '18px',
                                                borderRadius: '12px',
                                                background: 'var(--acc)',
                                                color: '#fff',
                                                border: '1px solid var(--acc)'
                                            }, children: isSubmitting
                                                ? 'Please wait…'
                                                : activeMode === 'signin'
                                                    ? 'Sign in'
                                                    : activeMode === 'signup'
                                                        ? 'Create account'
                                                        : 'Send reset link' })] }), activeMode === 'signup' && (_jsxs("p", { className: "help", style: { marginTop: '14px' }, children: ["Already registered?", ' ', _jsx("button", { type: "button", onClick: () => {
                                                setActiveMode('signin');
                                                setRoute('signin');
                                            }, style: { color: 'var(--acc)', border: 0, background: 'none', cursor: 'pointer', padding: 0 }, children: "Sign in" })] })), activeMode === 'forgot' && (_jsx("p", { className: "help", style: { marginTop: '14px' }, children: _jsx("button", { type: "button", onClick: () => {
                                            setActiveMode('signin');
                                            setRoute('signin');
                                        }, style: { color: 'var(--acc)', border: 0, background: 'none', cursor: 'pointer', padding: 0 }, children: "Back to sign in" }) })), _jsx("div", { style: { marginTop: '20px', textAlign: 'center' }, children: _jsx("button", { type: "button", onClick: () => setRoute('landing'), style: { color: 'var(--mute)', fontSize: '13px', border: 0, background: 'none', cursor: 'pointer', padding: 0 }, children: "\u2190 Return to Landing Page" }) }), _jsx("div", { className: "note", children: "Visual prototype. No authentication or account creation takes place." })] })) })] }), _jsxs("aside", { className: "auth-wrap r", "aria-label": "About AEGIS", children: [_jsx("h2", { children: "Your AI workforce, under your control." }), _jsx("p", { children: "AEGIS plans and runs multi-step work, and keeps risky actions behind policy and human approval." }), _jsxs("ul", { children: [_jsxs("li", { children: [_jsx("i", { "aria-hidden": "true", children: "1" }), _jsxs("div", { children: [_jsx("b", { children: "Policy decides" }), _jsx("span", { children: "Every tool call goes through the Policy Engine." })] })] }), _jsxs("li", { children: [_jsx("i", { "aria-hidden": "true", children: "2" }), _jsxs("div", { children: [_jsx("b", { children: "Approval for risky actions" }), _jsx("span", { children: "High-risk runs pause until a person decides." })] })] }), _jsxs("li", { children: [_jsx("i", { "aria-hidden": "true", children: "3" }), _jsxs("div", { children: [_jsx("b", { children: "Everything is recorded" }), _jsx("span", { children: "Tool calls, approvals and decisions write audit records." })] })] })] }), _jsxs("svg", { className: "deco", viewBox: "0 0 300 300", fill: "none", "aria-hidden": "true", children: [_jsx("path", { className: "flow", d: "M10 70C110 70 90 160 150 160S210 250 295 250", stroke: "#5B5CE2", strokeWidth: "3" }), _jsx("path", { d: "M160 60 80 94v62c0 50 36 80 80 94 44-14 80-44 80-94V94l-80-34Z", fill: "#fff", fillOpacity: ".8", stroke: "#5B5CE2", strokeWidth: "3" }), _jsx("path", { d: "M120 178l40-62 40 62", stroke: "#171927", strokeWidth: "4", strokeLinecap: "round" }), _jsx("circle", { cx: "120", cy: "178", r: "7", fill: "#438CFF" }), _jsx("circle", { cx: "160", cy: "116", r: "7", fill: "#5B5CE2" }), _jsx("circle", { cx: "200", cy: "178", r: "7", fill: "#A78BFA" })] })] })] }));
};
