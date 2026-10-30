import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import React from 'react';
const BADGE_MAP = {
    ok: { cls: 'ok', symbol: '✓' },
    run: { cls: 'in', symbol: '●' },
    wait: { cls: 'wt', symbol: '⏸' },
    bad: { cls: 'er', symbol: '✕' },
    off: { cls: 'nu', symbol: '○' },
    blk: { cls: 'er', symbol: '⛔' }
};
export const Badge = ({ variant, text, icon, className = '' }) => {
    const config = BADGE_MAP[variant] || BADGE_MAP.off;
    const displayIcon = icon !== undefined ? icon : config.symbol;
    return (_jsxs("span", { className: `badge ${config.cls} ${className}`, children: [displayIcon && _jsx("span", { "aria-hidden": "true", children: displayIcon }), text] }));
};
