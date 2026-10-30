import { INITIAL_TASKS, INITIAL_TOOLS, INITIAL_AUDIT_EVENTS, INITIAL_MEMORY } from '../data/mockData';
const STORAGE_KEYS = {
    TASKS: 'aegis_tasks',
    TOOLS: 'aegis_tools',
    AUDIT: 'aegis_audit',
    MEMORY: 'aegis_memory'
};
export class ClientDataService {
    // Tasks
    async getTasks() {
        const stored = localStorage.getItem(STORAGE_KEYS.TASKS);
        if (stored) {
            try {
                return JSON.parse(stored);
            }
            catch (e) { }
        }
        localStorage.setItem(STORAGE_KEYS.TASKS, JSON.stringify(INITIAL_TASKS));
        return INITIAL_TASKS;
    }
    async createTask(objective, domain) {
        const newTask = {
            id: `t-${105 + Math.floor(Math.random() * 890)}`,
            objective,
            domain,
            status: 'Running',
            statusVariant: 'run',
            createdAt: 'Just now',
            steps: [
                { name: 'Planner created steps', status: 'ok', note: '0.3 s' },
                { name: 'Policy Engine verified tool safety', status: 'ok', note: 'verified' },
                { name: 'Sandboxed execution initiated', status: 'run', note: 'in progress' }
            ]
        };
        const tasks = await this.getTasks();
        const updated = [newTask, ...tasks];
        localStorage.setItem(STORAGE_KEYS.TASKS, JSON.stringify(updated));
        await this.logAuditEvent(`Task ${newTask.id} created: "${objective.slice(0, 30)}..."`, 'planner');
        return newTask;
    }
    async deleteTask(id) {
        const tasks = await this.getTasks();
        const filtered = tasks.filter(t => t.id !== id);
        localStorage.setItem(STORAGE_KEYS.TASKS, JSON.stringify(filtered));
        await this.logAuditEvent(`Task ${id} deleted by operator`, 'operator');
        return true;
    }
    // Tools
    async getTools() {
        const stored = localStorage.getItem(STORAGE_KEYS.TOOLS);
        if (stored) {
            try {
                return JSON.parse(stored);
            }
            catch (e) { }
        }
        localStorage.setItem(STORAGE_KEYS.TOOLS, JSON.stringify(INITIAL_TOOLS));
        return INITIAL_TOOLS;
    }
    async revokeTool(name) {
        const tools = await this.getTools();
        const updated = tools.map(t => t.name === name
            ? { ...t, validation: 'Revoked', validationVariant: 'blk', revoked: true }
            : t);
        localStorage.setItem(STORAGE_KEYS.TOOLS, JSON.stringify(updated));
        await this.logAuditEvent(`Tool ${name} revoked by security officer`, 'policy');
        return updated;
    }
    async enableTool(name) {
        const tools = await this.getTools();
        const updated = tools.map(t => t.name === name
            ? { ...t, validation: 'Validated', validationVariant: 'ok', revoked: false }
            : t);
        localStorage.setItem(STORAGE_KEYS.TOOLS, JSON.stringify(updated));
        await this.logAuditEvent(`Tool ${name} reinstated to active registry`, 'policy');
        return updated;
    }
    async promoteTool(name) {
        const tools = await this.getTools();
        const existing = tools.find(t => t.name === name);
        let updated;
        if (existing) {
            updated = tools.map(t => t.name === name
                ? { ...t, validation: 'Promoted', validationVariant: 'ok', version: 'v2' }
                : t);
        }
        else {
            const newTool = {
                name,
                origin: 'forged',
                version: 'v1',
                risk: 'Medium',
                validation: 'Promoted',
                validationVariant: 'ok'
            };
            updated = [newTool, ...tools];
        }
        localStorage.setItem(STORAGE_KEYS.TOOLS, JSON.stringify(updated));
        await this.logAuditEvent(`Forged tool ${name} promoted to platform library`, 'human_reviewer');
        return updated;
    }
    // Memory
    async getMemory() {
        const stored = localStorage.getItem(STORAGE_KEYS.MEMORY);
        if (stored) {
            try {
                return JSON.parse(stored);
            }
            catch (e) { }
        }
        const initialWithIds = INITIAL_MEMORY.map((m, i) => ({
            id: `mem-${i + 1}`,
            record: m.record,
            type: m.type,
            updated: m.updated
        }));
        localStorage.setItem(STORAGE_KEYS.MEMORY, JSON.stringify(initialWithIds));
        return initialWithIds;
    }
    async addMemory(record, type) {
        const mems = await this.getMemory();
        const newRecord = {
            id: `mem-${Date.now()}`,
            record,
            type,
            updated: 'Just now'
        };
        const updated = [newRecord, ...mems];
        localStorage.setItem(STORAGE_KEYS.MEMORY, JSON.stringify(updated));
        await this.logAuditEvent(`Project memory updated with new ${type}`, 'critic');
        return updated;
    }
    // Audit Events
    async getAuditEvents() {
        const stored = localStorage.getItem(STORAGE_KEYS.AUDIT);
        if (stored) {
            try {
                return JSON.parse(stored);
            }
            catch (e) { }
        }
        const initialWithIds = INITIAL_AUDIT_EVENTS.map((a, i) => ({
            id: `aud-${i + 1}`,
            time: a.time,
            event: a.event,
            actor: a.actor
        }));
        localStorage.setItem(STORAGE_KEYS.AUDIT, JSON.stringify(initialWithIds));
        return initialWithIds;
    }
    async logAuditEvent(event, actor) {
        const now = new Date();
        const timeStr = `${now.getHours().toString().padStart(2, '0')}:${now
            .getMinutes()
            .toString()
            .padStart(2, '0')}`;
        const newEvent = {
            id: `aud-${Date.now()}`,
            time: timeStr,
            event,
            actor
        };
        const events = await this.getAuditEvents();
        const updated = [newEvent, ...events.slice(0, 49)];
        localStorage.setItem(STORAGE_KEYS.AUDIT, JSON.stringify(updated));
        return updated;
    }
    // Jev Simulation
    async queryJev(type, statement) {
        if (type === 'Noul') {
            const isHighRisk = statement.toLowerCase().includes('delete') ||
                statement.toLowerCase().includes('exec') ||
                statement.toLowerCase().includes('live') ||
                statement.toLowerCase().includes('risk') ||
                statement.toLowerCase().includes('billing');
            const prob = isHighRisk ? 0.91 : 0.18;
            return {
                answer: isHighRisk ? 'yes' : 'no',
                confidence: prob,
                escalated: prob < 0.8,
                reason: isHighRisk
                    ? 'Proposed call modifies or reads external network assets'
                    : 'Standard read-only verified operation'
            };
        }
        else if (type === 'Choice') {
            return {
                options: ['claude-3-5-sonnet', 'gemini-1.5-pro', 'groq-llama-3.3-70b'],
                chosen: 'claude-3-5-sonnet',
                confidence: 0.88,
                escalated: false
            };
        }
        else {
            return {
                score: 4,
                scale: '1 to 5',
                confidence: 0.84,
                escalated: false
            };
        }
    }
}
export const api = new ClientDataService();
