import { jsx as _jsx, Fragment as _Fragment, jsxs as _jsxs } from "react/jsx-runtime";
import React from 'react';
import { useApp } from './context/AppContext';
import { AppShell } from './components/layout/AppShell';
import { LandingPage } from './views/landing/LandingPage';
import { AuthView } from './views/app/AuthView';
import { Toast } from './components/common/Toast';
import { SignInModal } from './components/modals/SignInModal';
export const App = () => {
    const { currentRoute, toastMessage, activeModal } = useApp();
    if (currentRoute === 'landing') {
        return (_jsxs(_Fragment, { children: [_jsx(LandingPage, {}), _jsx(Toast, { message: toastMessage }), activeModal === 'signin' && _jsx(SignInModal, {})] }));
    }
    if (currentRoute === 'signin' || currentRoute === 'signup' || currentRoute === 'forgot') {
        return (_jsxs(_Fragment, { children: [_jsx(AuthView, { mode: currentRoute }), _jsx(Toast, { message: toastMessage })] }));
    }
    return _jsx(AppShell, {});
};
