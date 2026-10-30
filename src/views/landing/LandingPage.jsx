import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import React, { useEffect } from 'react';
import { LandingNav } from './LandingNav';
import { HeroSection } from './HeroSection';
import { ProductSection } from './ProductSection';
import { JevSection } from './JevSection';
import { OrchestrationSection } from './OrchestrationSection';
import { ForgeSection } from './ForgeSection';
import { SecuritySection } from './SecuritySection';
import { InteractivePlatformSection } from './InteractivePlatformSection';
import { DomainsSection } from './DomainsSection';
import { ArchitectureSection } from './ArchitectureSection';
import { LandingFooter } from './LandingFooter';
export const LandingPage = () => {
    useEffect(() => {
        document.body.classList.add('landing-mode');
        return () => {
            document.body.classList.remove('landing-mode');
        };
    }, []);
    return (_jsxs("div", { style: { background: 'var(--bg)', minHeight: '100vh', color: 'var(--ink)' }, children: [_jsx(LandingNav, {}), _jsxs("main", { children: [_jsx(HeroSection, {}), _jsx(ProductSection, {}), _jsx(JevSection, {}), _jsx(OrchestrationSection, {}), _jsx(ForgeSection, {}), _jsx(SecuritySection, {}), _jsx(InteractivePlatformSection, {}), _jsx(DomainsSection, {}), _jsx(ArchitectureSection, {})] }), _jsx(LandingFooter, {})] }));
};
