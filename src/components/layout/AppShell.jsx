import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import React from 'react';
import { useApp } from '../../context/AppContext';
import { Sidebar } from './Sidebar';
import { TopHeader } from './TopHeader';
import { Toast } from '../common/Toast';
import { NewTaskModal } from '../modals/NewTaskModal';
import { RevokeModal } from '../modals/RevokeModal';
import { DescribeToolModal } from '../modals/DescribeToolModal';
import { SignInModal } from '../modals/SignInModal';
import { HomeView } from '../../views/app/HomeView';
import { DashboardView } from '../../views/app/DashboardView';
import { TasksView } from '../../views/app/TasksView';
import { AgentsView } from '../../views/app/AgentsView';
import { JevView } from '../../views/app/JevView';
import { ToolForgeView } from '../../views/app/ToolForgeView';
import { ToolsView } from '../../views/app/ToolsView';
import { MemoryView } from '../../views/app/MemoryView';
import { EvaluationView } from '../../views/app/EvaluationView';
import { SecurityView } from '../../views/app/SecurityView';
import { ModelsView } from '../../views/app/ModelsView';
import { SettingsView } from '../../views/app/SettingsView';
import { UiStatesView } from '../../views/app/UiStatesView';
import { NotFoundView } from '../../views/app/NotFoundView';
export const AppShell = () => {
    const { currentRoute, toastMessage, activeModal } = useApp();
    const renderView = () => {
        switch (currentRoute) {
            case 'home':
                return _jsx(HomeView, {});
            case 'dash':
                return _jsx(DashboardView, {});
            case 'tasks':
                return _jsx(TasksView, {});
            case 'agents':
                return _jsx(AgentsView, {});
            case 'jev':
                return _jsx(JevView, {});
            case 'forge':
                return _jsx(ToolForgeView, {});
            case 'tools':
                return _jsx(ToolsView, {});
            case 'memory':
                return _jsx(MemoryView, {});
            case 'eval':
                return _jsx(EvaluationView, {});
            case 'security':
                return _jsx(SecurityView, {});
            case 'models':
                return _jsx(ModelsView, {});
            case 'settings':
                return _jsx(SettingsView, {});
            case 'states':
                return _jsx(UiStatesView, {});
            default:
                return _jsx(NotFoundView, {});
        }
    };
    return (_jsxs(_Fragment, { children: [_jsxs("div", { className: "shell", children: [_jsx(Sidebar, {}), _jsxs("div", { className: "mainc", children: [_jsx(TopHeader, {}), _jsx("main", { className: "page", children: renderView() })] })] }), _jsx(Toast, { message: toastMessage }), activeModal === 'newtask' && _jsx(NewTaskModal, {}), activeModal === 'revoke' && _jsx(RevokeModal, {}), activeModal === 'gap' && _jsx(DescribeToolModal, {}), activeModal === 'signin' && _jsx(SignInModal, {})] }));
};
