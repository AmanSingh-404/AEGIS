import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import React, { useState } from 'react';
import { INITIAL_EVAL_RUNS } from '../../data/mockData';
import { Badge } from '../../components/common/Badge';
import { useApp } from '../../context/AppContext';
export const EvaluationView = () => {
    const { showToast } = useApp();
    const [runs, setRuns] = useState(INITIAL_EVAL_RUNS);
    const [runningSuite, setRunningSuite] = useState(false);
    const handleRunEvaluation = () => {
        setRunningSuite(true);
        showToast('Running benchmark evaluation suite across 120 test cases...');
        setTimeout(() => {
            const newRun = {
                run: `e-${13 + runs.length}`,
                suite: 'Benchmark: Agent Robustness & Safety',
                result: 'Pass',
                resultVariant: 'ok'
            };
            setRuns(prev => [newRun, ...prev]);
            setRunningSuite(false);
            showToast('Evaluation suite completed: 100% safety checks passed!');
        }, 1200);
    };
    return (_jsxs(_Fragment, { children: [_jsxs("div", { className: "head", children: [_jsxs("div", { children: [_jsx("div", { className: "crumb", children: "Demo workspace / Evaluation lab" }), _jsx("h1", { children: "Evaluation lab" }), _jsx("p", { children: "Continuous evaluation of agent performance, latency, and decision calibration." })] }), _jsx("div", { children: _jsx("button", { type: "button", className: "btn p", onClick: handleRunEvaluation, disabled: runningSuite, children: runningSuite ? 'Running suite...' : '▶ Run Evaluation Suite' }) })] }), _jsxs("div", { className: "g g4", children: [_jsxs("div", { className: "card kpi", children: [_jsx("b", { children: "82%" }), _jsx("span", { children: "Task success" })] }), _jsxs("div", { className: "card kpi", children: [_jsx("b", { children: "14 s" }), _jsx("span", { children: "Median latency" })] }), _jsxs("div", { className: "card kpi", children: [_jsx("b", { children: "0" }), _jsx("span", { children: "Unsafe promotions (target)" })] }), _jsxs("div", { className: "card kpi", children: [_jsx("b", { children: "0.07" }), _jsx("span", { children: "Calibration error" })] })] }), _jsxs("div", { className: "g g2", style: { marginTop: '16px' }, children: [_jsxs("div", { className: "card", children: [_jsx("h3", { children: "Evaluation runs" }), _jsx("div", { className: "tw", children: _jsxs("table", { children: [_jsx("thead", { children: _jsxs("tr", { children: [_jsx("th", { scope: "col", children: "Run" }), _jsx("th", { scope: "col", children: "Suite" }), _jsx("th", { scope: "col", children: "Result" })] }) }), _jsx("tbody", { children: runs.map(run => (_jsxs("tr", { children: [_jsx("td", { children: _jsx("span", { className: "mono", children: run.run }) }), _jsx("td", { children: run.suite }), _jsx("td", { children: _jsx(Badge, { variant: run.resultVariant, text: run.result }) })] }, run.run))) })] }) })] }), _jsxs("div", { className: "card", children: [_jsx("h3", { children: "Research metrics" }), _jsx("p", { style: { margin: '0 0 6px', fontWeight: 500 }, children: "Jev Decision Layer" }), _jsxs("div", { className: "row", children: [_jsx("span", { children: "Escalation rate" }), _jsx("span", { children: "18%" })] }), _jsxs("div", { className: "row", children: [_jsx("span", { children: "Jev / LLM agreement" }), _jsx("span", { children: "91%" })] }), _jsx("p", { style: { margin: '16px 0 6px', fontWeight: 500 }, children: "Tool Forge Performance" }), _jsxs("div", { className: "row", children: [_jsx("span", { children: "Sandbox pass rate" }), _jsx("span", { children: "75%" })] }), _jsxs("div", { className: "row", children: [_jsx("span", { children: "Time to verified tool" }), _jsx("span", { children: "6 min" })] })] })] })] }));
};
