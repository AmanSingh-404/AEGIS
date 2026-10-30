import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { Badge } from '../../components/common/Badge';
import { api } from '../../services/api';
export const JevView = () => {
    const { jevThreshold, setJevThreshold, showToast } = useApp();
    const [activeTab, setActiveTab] = useState('Noul');
    const [customInput, setCustomInput] = useState('');
    const [evalResult, setEvalResult] = useState(null);
    const [evaluating, setEvaluating] = useState(false);
    const tabContents = {
        Noul: (_jsxs("div", { children: ["Statement: \u201CThis proposed tool call is high-risk.\u201D", _jsx("br", {}), _jsx("pre", { className: "mono", style: { marginTop: '8px' }, children: `state: tool=billing_api_client
action: first live call
answer: yes
probability: 0.91 (confidence 0.91)` })] })),
        Choice: (_jsxs("div", { children: ["Question: which model should handle this task?", _jsx("pre", { className: "mono", style: { marginTop: '8px' }, children: `options: model-a, model-b, model-c
probabilities: .62 / .24 / .14
confidence: 0.62 → escalated` })] })),
        Score: (_jsxs("div", { children: ["Question: rate this draft against levels 1 to 5", _jsx("pre", { className: "mono", style: { marginTop: '8px' }, children: `score: 4
confidence: 0.84 → skip full LLM judge` })] }))
    };
    const handleEvaluateCustom = async () => {
        if (!customInput.trim())
            return;
        setEvaluating(true);
        const res = await api.queryJev(activeTab, customInput);
        setEvalResult(res);
        setEvaluating(false);
        showToast(`Jev evaluated: Confidence ${(res.confidence * 100).toFixed(0)}%`);
    };
    return (_jsxs(_Fragment, { children: [_jsx("div", { className: "head", children: _jsxs("div", { children: [_jsx("div", { className: "crumb", children: "Demo workspace / Jev decisions" }), _jsx("h1", { children: "Jev decision layer" }), _jsx("p", { children: "Structured, typed System 1 decisions. Advisory only: deterministic Policy Engine and humans decide." })] }) }), _jsxs("div", { className: "g g2", children: [_jsxs("div", { className: "card", children: [_jsx("div", { className: "tabs", role: "tablist", children: ['Noul', 'Choice', 'Score'].map(tab => (_jsx("button", { type: "button", role: "tab", "aria-selected": activeTab === tab, onClick: () => {
                                        setActiveTab(tab);
                                        setEvalResult(null);
                                    }, children: tab }, tab))) }), _jsx("div", { style: { marginBottom: '16px' }, children: tabContents[activeTab] }), _jsxs("div", { style: { padding: '14px', background: 'var(--soft)', borderRadius: '10px', marginBottom: '16px', border: '1px solid var(--line)' }, children: [_jsxs("label", { htmlFor: "jevin", style: { marginTop: 0 }, children: ["Test Jev ", activeTab, " Primitive"] }), _jsx("input", { id: "jevin", value: customInput, onChange: e => setCustomInput(e.target.value), placeholder: activeTab === 'Noul' ? 'e.g. Is executing database migrations high risk?' : 'e.g. Rate relevance of generated summary', onKeyDown: e => e.key === 'Enter' && handleEvaluateCustom() }), _jsx("button", { type: "button", className: "btn p", style: { marginTop: '8px', height: '32px', fontSize: '12.5px' }, onClick: handleEvaluateCustom, disabled: evaluating, children: evaluating ? 'Evaluating...' : 'Query Jev Model' }), evalResult && (_jsx("pre", { className: "mono", style: { marginTop: '10px', fontSize: '12px' }, children: JSON.stringify(evalResult, null, 2) }))] }), _jsx("h3", { children: "Decision history" }), _jsx("div", { className: "tw", children: _jsxs("table", { children: [_jsx("thead", { children: _jsxs("tr", { children: [_jsx("th", { scope: "col", children: "Type" }), _jsx("th", { scope: "col", children: "Answer" }), _jsx("th", { scope: "col", children: "Conf." }), _jsx("th", { scope: "col", children: "Escalated" }), _jsx("th", { scope: "col", children: "Agreed" })] }) }), _jsxs("tbody", { children: [_jsxs("tr", { children: [_jsx("td", { children: "Noul" }), _jsx("td", { children: "High-risk" }), _jsx("td", { children: "0.91" }), _jsx("td", { children: "No" }), _jsx("td", { children: "n/a" })] }), _jsxs("tr", { children: [_jsx("td", { children: "Choice" }), _jsx("td", { children: "model-b" }), _jsx("td", { children: "0.62" }), _jsx("td", { children: _jsx(Badge, { variant: "wait", text: "Yes" }) }), _jsx("td", { children: "Yes" })] }), _jsxs("tr", { children: [_jsx("td", { children: "Score" }), _jsx("td", { children: "4" }), _jsx("td", { children: "0.84" }), _jsx("td", { children: "No" }), _jsx("td", { children: "Sampled: yes" })] })] })] }) })] }), _jsxs("div", { className: "card", children: [_jsx("h3", { children: "Cascade (System 1 \u2192 System 2)" }), _jsx("p", { style: { color: 'var(--mute)', marginTop: 0 }, children: "At or above threshold, act on Jev's answer. Below, escalate to the LLM or a human." }), _jsxs("label", { htmlFor: "th", children: ["Threshold for Noul: ", _jsx("span", { id: "thv", className: "mono", children: jevThreshold.toFixed(2) })] }), _jsx("input", { id: "th", type: "range", min: "50", max: "99", value: Math.round(jevThreshold * 100), onChange: e => setJevThreshold(Number(e.target.value) / 100) }), _jsx("p", { className: "help", children: "Lowering it raises escalation less, raising it escalates more." }), _jsx("h3", { style: { marginTop: '18px' }, children: "Policy context" }), _jsxs("div", { className: "row", children: [_jsx("span", { children: "Deterministic policy" }), _jsx(Badge, { variant: "ok", text: "Always final" })] }), _jsxs("div", { className: "row", children: [_jsx("span", { children: "Human approval above risk threshold" }), _jsx(Badge, { variant: "wait", text: "Required" })] }), _jsxs("div", { className: "row", children: [_jsx("span", { children: "Fallback provider" }), _jsx(Badge, { variant: "off", text: "LocalDecisionProvider (standby)" })] }), _jsx("p", { className: "help", children: "Supplied state is treated as data, so crafted text can sway Jev. That is why it is never the sole gate." })] })] })] }));
};
