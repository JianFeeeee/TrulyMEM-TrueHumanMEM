export interface ActivityRecord {
    id: number;
    timestamp: number;
    action: string;
    toolName: string;
    entity: string;
    detail: string;
}

export class ActivityRecorder {
    private records: ActivityRecord[] = [];
    private nextId: number = 1;

    record(action: string, toolName: string, entity: string, detail?: string): void {
        const record: ActivityRecord = {
            id: this.nextId++,
            timestamp: Date.now() / 1000,
            action: action,
            toolName: toolName,
            entity: entity,
            detail: detail || ""
        };
        this.records.push(record);
    }

    getAll(): ActivityRecord[] {
        return this.records.slice();
    }

    clear(): void {
        this.records = [];
        this.nextId = 1;
    }

    getSummary(): Map<string, number> {
        const summary: Map<string, number> = new Map<string, number>();
        for (const record of this.records) {
            const currentCount: number = summary.get(record.action) ?? 0;
            summary.set(record.action, currentCount + 1);
        }
        return summary;
    }
}
