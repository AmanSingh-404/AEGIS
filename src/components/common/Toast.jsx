import { jsx as _jsx } from "react/jsx-runtime";
import React from 'react';
export const Toast = ({ message }) => {
    return (_jsx("div", { className: `toast ${message ? 'on' : ''}`, role: "status", children: message }));
};
