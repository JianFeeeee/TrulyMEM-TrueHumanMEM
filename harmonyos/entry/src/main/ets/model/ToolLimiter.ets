export class ToolLimiter {
    private personaUpdateMax: number = 1;
    private taskUpdateMax: number = 5;
    private memoryQueryMax: number = 20;
    private memoryUpdateMax: number = 10;
    private personaUpdate: number = 0;
    private taskUpdate: number = 0;
    private memoryQuery: number = 0;
    private memoryUpdate: number = 0;

    canCall(toolName: string): [boolean, string] {
        const [cat, op]: [string, string] = this.classifyTool(toolName);
        if (cat === 'persona' && this.personaUpdate >= this.personaUpdateMax) {
            return [false, `人设修改已达上限(${this.personaUpdateMax}次)`];
        }
        if (cat === 'task' && this.taskUpdate >= this.taskUpdateMax) {
            return [false, `任务修改已达上限(${this.taskUpdateMax}次)`];
        }
        if (cat === 'memory' && op === 'query' && this.memoryQuery >= this.memoryQueryMax) {
            return [false, `记忆查询已达上限(${this.memoryQueryMax}次)`];
        }
        if (cat === 'memory' && op === 'update' && this.memoryUpdate >= this.memoryUpdateMax) {
            return [false, `记忆修改已达上限(${this.memoryUpdateMax}次)`];
        }
        return [true, "允许调用"];
    }

    recordCall(toolName: string): void {
        const [cat, op]: [string, string] = this.classifyTool(toolName);
        if (cat === 'persona') {
            this.personaUpdate++;
        } else if (cat === 'task') {
            this.taskUpdate++;
        } else if (cat === 'memory') {
            if (op === 'query') {
                this.memoryQuery++;
            } else {
                this.memoryUpdate++;
            }
        }
    }

    private classifyTool(toolName: string): [string, string] {
        if (toolName === 'persona_update' || toolName === 'persona_clear') {
            return ['persona', 'update'];
        }
        if (toolName === 'task_create' || toolName === 'task_set_state' || toolName === 'task_delete' || toolName === 'task_link_info') {
            return ['task', 'update'];
        }
        if (toolName === 'memory_recall') {
            return ['memory', 'query'];
        }
        if (toolName === 'memory_commit' || toolName === 'memory_purge' || toolName === 'memory_archive' || toolName === 'memory_cleanup') {
            return ['memory', 'update'];
        }
        if (toolName === 'memory_introspect' || toolName === 'context_rewrite') {
            return ['memory', 'query'];
        }
        return ['memory', 'update'];
    }

    getSummary(): string {
        const lines: string[] = [
            `人设图: 修改${this.personaUpdate}/${this.personaUpdateMax}次`,
            `工作记忆链: 修改${this.taskUpdate}/${this.taskUpdateMax}次`,
            `一般记忆: 查询${this.memoryQuery}/${this.memoryQueryMax}次, 修改${this.memoryUpdate}/${this.memoryUpdateMax}次`
        ];
        return lines.join('\n');
    }

    reset(): void {
        this.personaUpdate = 0;
        this.taskUpdate = 0;
        this.memoryQuery = 0;
        this.memoryUpdate = 0;
    }
}
