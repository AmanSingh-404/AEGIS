import { jsx as _jsx } from "react/jsx-runtime";
import React, { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../services/api';
const AppContext = createContext(undefined);
export const AppProvider = ({ children }) => {
    // Theme: checks localStorage or defaults to 'light'
    const [theme, setTheme] = useState(() => {
        const saved = localStorage.getItem('aegis_theme');
        return saved || 'light';
    });
    useEffect(() => {
        document.documentElement.setAttribute('data-theme', theme);
        document.body.setAttribute('data-theme', theme);
        localStorage.setItem('aegis_theme', theme);
    }, [theme]);
    const toggleTheme = () => {
        setTheme(prev => (prev === 'light' ? 'dark' : 'light'));
    };
    // Route: Default is 'landing' so user sees the Landing Page when opening the website!
    const [currentRoute, setCurrentRoute] = useState(() => {
        const hash = window.location.hash.replace('#/', '').replace('#', '');
        if (hash)
            return hash;
        return 'landing'; // Default to landing page on root visit!
    });
    useEffect(() => {
        const handleHash = () => {
            const hash = window.location.hash.replace('#/', '').replace('#', '');
            if (!hash) {
                setCurrentRoute('landing');
            }
            else {
                setCurrentRoute(hash);
            }
        };
        window.addEventListener('hashchange', handleHash);
        return () => window.removeEventListener('hashchange', handleHash);
    }, []);
    const setRoute = (route) => {
        setCurrentRoute(route);
        window.location.hash = `#/${route}`;
    };
    // State entities
    const [pendingApprovalsCount, setPendingApprovalsCount] = useState(2);
    const [billingApproved, setBillingApproved] = useState(null);
    const [tasks, setTasks] = useState([]);
    const [tools, setTools] = useState([]);
    const [auditEvents, setAuditEvents] = useState([]);
    const [memoryRecords, setMemoryRecords] = useState([]);
    const [jevThreshold, setJevThreshold] = useState(0.80);
    // Modals & Toast
    const [activeModal, setActiveModal] = useState(null);
    const [targetRevokeTool, setTargetRevokeTool] = useState(null);
    const [toastMessage, setToastMessage] = useState(null);
    // Load initial data from client data service
    useEffect(() => {
        const loadAll = async () => {
            const [tList, tlList, aList, mList] = await Promise.all([
                api.getTasks(),
                api.getTools(),
                api.getAuditEvents(),
                api.getMemory()
            ]);
            setTasks(tList);
            setTools(tlList);
            setAuditEvents(aList);
            setMemoryRecords(mList);
        };
        loadAll();
    }, []);
    const showToast = (msg) => {
        setToastMessage(msg);
        setTimeout(() => {
            setToastMessage(prev => (prev === msg ? null : prev));
        }, 2500);
    };
    const openModal = (modal, toolName) => {
        setActiveModal(modal);
        if (toolName) {
            setTargetRevokeTool(toolName);
        }
    };
    const closeModal = () => {
        setActiveModal(null);
        setTargetRevokeTool(null);
    };
    const approveBilling = async (approved) => {
        setBillingApproved(approved);
        setPendingApprovalsCount(prev => Math.max(0, prev - 1));
        await api.logAuditEvent(approved
            ? 'First live call approved for billing_api_client'
            : 'First live call rejected for billing_api_client', 'security_officer');
        const updatedAudit = await api.getAuditEvents();
        setAuditEvents(updatedAudit);
        showToast(approved
            ? 'Approved (demo): audit record written, run resumes.'
            : 'Rejected (demo): candidate kept unpromoted.');
    };
    const addNewTask = async (objective, domain) => {
        const created = await api.createTask(objective, domain);
        setTasks(prev => [created, ...prev]);
        const updatedAudit = await api.getAuditEvents();
        setAuditEvents(updatedAudit);
        showToast(`Task ${created.id} created & scheduled`);
        closeModal();
    };
    const deleteTask = async (id) => {
        await api.deleteTask(id);
        setTasks(prev => prev.filter(t => t.id !== id));
        showToast(`Task ${id} deleted`);
    };
    const confirmRevoke = async () => {
        if (targetRevokeTool) {
            const updated = await api.revokeTool(targetRevokeTool);
            setTools(updated);
            const updatedAudit = await api.getAuditEvents();
            setAuditEvents(updatedAudit);
            showToast(`Tool ${targetRevokeTool} revoked`);
        }
        closeModal();
    };
    const promoteTool = async (name) => {
        const updated = await api.promoteTool(name);
        setTools(updated);
        const updatedAudit = await api.getAuditEvents();
        setAuditEvents(updatedAudit);
        showToast(`Tool ${name} promoted to Registry`);
    };
    const addMemoryRecord = async (record, type) => {
        const updated = await api.addMemory(record, type);
        setMemoryRecords(updated);
        const updatedAudit = await api.getAuditEvents();
        setAuditEvents(updatedAudit);
        showToast('Memory record added');
    };
    const forgeNewCandidate = async (description) => {
        await api.logAuditEvent(`Tool Forge drafted new candidate: "${description.slice(0, 30)}..."`, 'tool_forge_agent');
        const updatedAudit = await api.getAuditEvents();
        setAuditEvents(updatedAudit);
        showToast('New candidate tool drafted & sandboxed');
        closeModal();
    };
    return (_jsx(AppContext.Provider, { value: {
            theme,
            toggleTheme,
            currentRoute,
            setRoute,
            pendingApprovalsCount,
            billingApproved,
            tasks,
            tools,
            auditEvents,
            memoryRecords,
            jevThreshold,
            setJevThreshold,
            activeModal,
            targetRevokeTool,
            toastMessage,
            showToast,
            openModal,
            closeModal,
            approveBilling,
            addNewTask,
            deleteTask,
            confirmRevoke,
            promoteTool,
            addMemoryRecord,
            forgeNewCandidate
        }, children: children }));
};
export const useApp = () => {
    const context = useContext(AppContext);
    if (!context) {
        throw new Error('useApp must be used within an AppProvider');
    }
    return context;
};
