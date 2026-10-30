export const INITIAL_TASKS = [
    {
        id: 't-104',
        objective: 'Reconcile billing against ledger',
        domain: 'Data Analysis',
        status: 'Awaiting approval',
        statusVariant: 'wait',
        createdAt: '10 min ago'
    },
    {
        id: 't-103',
        objective: 'Fix failing API tests',
        domain: 'Software Eng.',
        status: 'Done',
        statusVariant: 'ok',
        createdAt: '1 hour ago'
    },
    {
        id: 't-102',
        objective: 'Compare retrieval configs',
        domain: 'AI/ML Eng.',
        status: 'Running',
        statusVariant: 'run',
        createdAt: '2 hours ago'
    },
    {
        id: 't-101',
        objective: 'Parse malformed CSV',
        domain: 'Data Analysis',
        status: 'Failed',
        statusVariant: 'bad',
        createdAt: '3 hours ago'
    }
];
export const INITIAL_AGENTS = [
    {
        name: 'Planner',
        description: 'Breaks objectives into dependency-aware steps',
        tools: 'none',
        status: 'Available',
        statusVariant: 'ok'
    },
    {
        name: 'Researcher',
        description: 'Search, retrieve, cite',
        tools: 'web/search, document parsing',
        status: 'Idle',
        statusVariant: 'ok'
    },
    {
        name: 'Coder',
        description: 'Reads repos, proposes changes',
        tools: 'filesystem, GitHub',
        status: 'Running',
        statusVariant: 'run'
    },
    {
        name: 'Data Analyst',
        description: 'Sandboxed Python analysis',
        tools: 'python sandbox',
        status: 'Available',
        statusVariant: 'ok'
    },
    {
        name: 'Security',
        description: 'Defensive checks, red-team tests',
        tools: 'policy, sandbox',
        status: 'Available',
        statusVariant: 'ok'
    },
    {
        name: 'Critic',
        description: 'Judges results, flags capability gaps',
        tools: 'evaluation',
        status: 'Idle',
        statusVariant: 'ok'
    },
    {
        name: 'Repair',
        description: 'Diagnoses failures, retries (max 3)',
        tools: 'all via policy',
        status: 'Available',
        statusVariant: 'ok'
    },
    {
        name: 'Tool Forge Agent',
        description: 'Drafts candidate tools',
        tools: 'sandbox',
        status: 'Paused',
        statusVariant: 'wait'
    },
    {
        name: 'Decision Router',
        description: 'Calls Jev for typed decisions',
        tools: 'Jev provider',
        status: 'Available',
        statusVariant: 'ok'
    }
];
export const INITIAL_TOOLS = [
    {
        name: 'web/search',
        origin: 'registered',
        version: 'v1',
        risk: 'Low',
        validation: 'Validated',
        validationVariant: 'ok'
    },
    {
        name: 'github',
        origin: 'registered',
        version: 'v3',
        risk: 'High',
        validation: 'Approval required',
        validationVariant: 'ok'
    },
    {
        name: 'python_sandbox',
        origin: 'registered',
        version: 'v2',
        risk: 'Medium',
        validation: 'Validated',
        validationVariant: 'ok'
    },
    {
        name: 'fx_rate_fetch',
        origin: 'forged',
        version: 'v2',
        risk: 'Medium',
        validation: 'Promoted',
        validationVariant: 'ok'
    },
    {
        name: 'csv_dedupe',
        origin: 'forged',
        version: 'v1',
        risk: 'Low',
        validation: 'Rejected',
        validationVariant: 'bad'
    },
    {
        name: 'old_scraper',
        origin: 'forged',
        version: 'v1',
        risk: 'High',
        validation: 'Revoked',
        validationVariant: 'blk',
        revoked: true
    }
];
export const INITIAL_MEMORY = [
    {
        id: 'mem-1',
        record: 'Use pytest, not unittest',
        type: 'Convention',
        updated: '2 d ago'
    },
    {
        id: 'mem-2',
        record: 'Chunk size 512 beat 256 (demo)',
        type: 'Experiment',
        updated: '5 d ago'
    },
    {
        id: 'mem-3',
        record: 'Auth lives in core/policies',
        type: 'Architecture',
        updated: '1 w ago'
    }
];
export const INITIAL_PROVIDERS = [
    { provider: 'Groq', role: 'Fast agent work', status: 'Configured', statusVariant: 'ok' },
    { provider: 'Gemini', role: 'General reasoning', status: 'Not configured', statusVariant: 'off' },
    { provider: 'Mistral', role: 'Open-model tests', status: 'Not configured', statusVariant: 'off' },
    { provider: 'OpenRouter', role: 'Multi-model', status: 'Auth error', statusVariant: 'bad' },
    { provider: 'Ollama (local)', role: 'Fallback', status: 'Not running', statusVariant: 'off' },
    { provider: 'Jev', role: 'Decision layer', status: 'Early access', statusVariant: 'run' }
];
export const INITIAL_EVAL_RUNS = [
    { run: 'e-12', suite: 'Benchmark: Research', result: 'Pass', resultVariant: 'ok' },
    { run: 'e-11', suite: 'Security: injection set', result: 'Pass', resultVariant: 'ok' },
    { run: 'e-10', suite: 'Benchmark: Data Analysis', result: 'Regression', resultVariant: 'wait' }
];
export const INITIAL_AUDIT_EVENTS = [
    { id: 'aud-1', time: '10:41', event: 'Policy decision: needs approval', actor: 'policy' },
    { id: 'aud-2', time: '10:40', event: 'Sandbox run passed', actor: 'sandbox' },
    { id: 'aud-3', time: '10:38', event: 'Candidate drafted', actor: 'tool_forge_agent' }
];
export const INITIAL_BLOCKED_ACTIONS = [
    { action: 'os.system in candidate', reason: 'Static analysis hard-fail', state: 'Blocked' },
    { action: 'write outside workdir', reason: 'Filesystem scope', state: 'Blocked' }
];
export const DOMAIN_PLAN_MAP = {
    'Software Engineering': [
        'Coder',
        'filesystem, github',
        'Approval required before a PR is opened'
    ],
    'Research': [
        'Researcher',
        'web/search, document parsing',
        'No high-risk tools expected'
    ],
    'Data Analysis': [
        'Data Analyst',
        'python sandbox',
        'Sandboxed, no network by default'
    ],
    'AI/ML Engineering': [
        'AI/ML Engineer',
        'python sandbox, filesystem',
        'Code changes pass the Policy Engine'
    ],
    'AI Security': [
        'Security',
        'policy, sandbox',
        'Authorized defensive tests only'
    ]
};
