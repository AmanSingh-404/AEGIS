# AEGIS — Autonomous Engineering & Intelligent Governance System

A production-ready React + JavaScript implementation of the **AEGIS** platform, styled with Tailwind CSS and the existing custom design system.

---

## 🌟 Overview & Architecture

AEGIS is built with enterprise frontend standards:
- **Modular Component Design**: Every view, modal, section, and widget is decoupled into its own file.
- **Centralized State Management (`AppContext.jsx`)**: Reactive state for pending approvals, task creation, tool revocation, live Jev threshold adjustments, toast notifications, and seamless hash routing.
- **Styling**: Tailwind CSS utilities alongside custom styles for the platform's detailed design system.
- **Dual Presentation**:
  1. **Full Web Application** (`#/home`, `#/dash`, `#/tasks`, `#/agents`, `#/jev`, `#/forge`, `#/tools`, `#/memory`, `#/eval`, `#/security`, `#/models`, `#/settings`, `#/states`).
  2. **Marketing & Solutions Landing Page** (`#/landing`).
  3. **Authentication Flows** (`#/signin`, `#/forgot`).

---

## 📁 File Structure

```
c:\Users\hp\OneDrive\Desktop\AEGIS\
├── index.html
├── package.json
├── tailwind.config.js
├── postcss.config.js
├── vite.config.js
└── src/
    ├── main.jsx
    ├── App.jsx
    ├── context/
    │   └── AppContext.jsx            # Global state (routes, approvals, tasks, modals, toasts)
    ├── data/
    │   └── mockData.js               # Realistic data for tasks, agents, tools, audit events
    ├── styles/
    │   └── index.css                 # Exact design tokens, fonts, animations, and CSS vars
    ├── components/
    │   ├── common/
    │   │   ├── Logo.jsx              # AEGIS shield vector icon
    │   │   ├── Badge.jsx             # Status badges (ok, in, wt, er, nu, blk)
    │   │   ├── Icons.jsx             # Complete set of navigation & tool SVGs
    │   │   └── Toast.jsx             # Floating notification system
    │   ├── layout/
    │   │   ├── AppShell.jsx          # Outer container with desktop 28px card shell
    │   │   ├── Sidebar.jsx           # Vertical circular icon navigation with active dot
    │   │   └── TopHeader.jsx         # Top bar with dropdowns, notifications, and actions
    │   └── modals/
    │       ├── NewTaskModal.jsx      # Modal to configure and submit objectives
    │       ├── RevokeModal.jsx       # Safety confirmation modal to revoke tools
    │       ├── DescribeToolModal.jsx # Tool Forge drafting modal
    │       └── SignInModal.jsx       # Interactive landing sign-in modal
    └── views/
        ├── app/
        │   ├── HomeView.jsx          # Plan preview with live domain trace generator
        │   ├── DashboardView.jsx     # KPI metrics, live trace & agent activity
        │   ├── TasksView.jsx         # Searchable task registry with execution trace
        │   ├── AgentsView.jsx        # 9 Agent specifications with access policies
        │   ├── JevView.jsx           # Typed decision layer with live cascade slider
        │   ├── ToolForgeView.jsx     # Candidate tool inspection & gate validation
        │   ├── ToolsView.jsx         # Active & forged tools management
        │   ├── MemoryView.jsx        # Vector retrieval and project memory
        │   ├── EvaluationView.jsx    # Benchmarks & research calibration
        │   ├── SecurityView.jsx      # Approval queue, audit trail & policy rules
        │   ├── ModelsView.jsx        # Provider router and API key vault
        │   ├── SettingsView.jsx      # Multi-tab settings (Workspace, Policies, Account)
        │   ├── UiStatesView.jsx      # Skeleton, empty, error, and blocked patterns
        │   ├── AuthView.jsx          # Sign-in & password recovery with flow illustration
        │   └── NotFoundView.jsx      # 404 handler
        └── landing/
            ├── LandingPage.jsx       # Marketing layout assembler
            ├── LandingNav.jsx        # Sticky blur navigation
            ├── HeroSection.jsx       # Hero with animated flow SVG gate
            ├── ProductSection.jsx    # 5 Platform pillars
            ├── JevSection.jsx        # Decision primitives showcase
            ├── OrchestrationSection.jsx # 7-step pipeline timeline
            ├── ForgeSection.jsx      # Animated step pipeline & code/schema tabs
            ├── SecuritySection.jsx   # 6 Governance principles grid
            ├── InteractivePlatformSection.jsx # Embedded interactive mini-app
            ├── DomainsSection.jsx    # 5 MVP solution domains
            ├── ArchitectureSection.jsx # Complete system architecture SVG
            └── LandingFooter.jsx     # Conversion CTA & sitemap footer
```

---

## 🚀 How to Run

1. **Development Server**:
   ```bash
   npm run dev
   ```
   Opens `http://localhost:5173` in your browser.

2. **Production Build**:
   ```bash
   npm run build
   ```

3. **Preview Production Build**:
   ```bash
   npm run preview
   ```

---

## 🎯 Key Features Implemented

- **Same-to-same Design**: Typography (`Space Grotesk`, `Inter`, `JetBrains Mono`), exact color palette, shadows, borders, badges, SVG gates, and animation keyframes.
- **Interactive State**:
  - Approve or Reject high-risk tool calls with live updates across the Dashboard, Security Center, and Top Header notification badge.
  - Interactive "Preview plan" in the Home view that dynamically synthesizes agent pipelines based on selected domains.
  - Tool Forge candidate review with functional code/schema/sandbox/static analysis tabs.
  - Interactive Jev threshold slider updating confidence gate routing in real time.
  - Task creation modal adding live tasks into the Tasks and Dashboard tables.
  - Tool revocation modal disabling tools in the Tool Library.
  - Hash routing allowing direct bookmarking and navigation to any view (`#/home`, `#/dash`, `#/landing`, etc.).
