import { GraphDatabase } from './graph_database';
import type { RecallParams, CommitParams, PurgeParams, RecallResult, CommitResult, PurgeResult, MemoryStats } from './types';

export class MemoryService {
  private db: GraphDatabase;

  constructor(db: GraphDatabase) {
    this.db = db;
  }

  async recall(params: RecallParams): Promise<RecallResult> {
    return this.db.recall(params);
  }

  async commit(params: CommitParams): Promise<CommitResult> {
    return this.db.commit(params);
  }

  async purge(params: PurgeParams): Promise<PurgeResult> {
    return this.db.purge(params);
  }

  async introspect(): Promise<MemoryStats> {
    return this.db.introspect();
  }

  async archive(days: number = 30): Promise<{ archived: number }> {
    return this.db.archive(days);
  }

  async cleanup(dryRun: boolean = true): Promise<{ deleted_relations: number; deleted_entities: number; details?: string[] }> {
    return this.db.cleanup(dryRun);
  }

  async updatePersona(params: { attributes: Array<{ attribute: string; value: string }>; mode?: 'merge' | 'replace' }): Promise<{ status: string; updatedAttributes: number }> {
    const { attributes, mode = 'merge' } = params;

    if (mode === 'replace') {
      await this.db.purge({
        criteria: { subject: 'AI' },
        mode: 'soft'
      });
    }

    const triplets = attributes.map(attr => ({
      subject: 'AI',
      relation: attr.attribute,
      object: attr.value,
      confidence: 1.0
    }));

    await this.db.commit({ triplets });

    return { status: 'success', updatedAttributes: attributes.length };
  }

  async clearPersona(params: { confirm: boolean }): Promise<{ status: string; deletedCount: number }> {
    if (params.confirm === false) {
      return { status: 'cancelled', deletedCount: 0 };
    }

    const result = await this.db.purge({
      criteria: { subject: 'AI' },
      mode: 'soft'
    });

    return { status: 'success', deletedCount: result.deleted };
  }

  async createTask(params: { task_id: string; description: string; info_nodes?: string[] | undefined }): Promise<{ status: string; taskId: string }> {
    const { task_id, description, info_nodes = [] } = params;

    await this.db.commit({
      triplets: [
        { subject: task_id, relation: 'is_type', object: 'TaskNode' },
        { subject: task_id, relation: 'has_description', object: description },
        { subject: task_id, relation: 'HAS_STATE', object: 'State_进行中' }
      ]
    });

    if (info_nodes.length > 0) {
      await this.db.commit({
        triplets: info_nodes.map(node => ({
          subject: task_id,
          relation: 'CONTAINS_INFO',
          object: node
        }))
      });
    }

    return { status: 'success', taskId: task_id };
  }

  async setTaskState(params: { task_id: string; state: string }): Promise<{ status: string; newState: string }> {
    const { task_id, state } = params;

    await this.db.purge({
      criteria: { subject: task_id, relation: 'HAS_STATE' },
      mode: 'soft'
    });

    await this.db.commit({
      triplets: [{ subject: task_id, relation: 'HAS_STATE', object: `State_${state}` }]
    });

    return { status: 'success', newState: state };
  }

  async deleteTask(params: { task_id: string }): Promise<{ status: string; taskId: string }> {
    const { task_id } = params;

    await this.db.purge({
      criteria: { subject: task_id },
      mode: 'soft'
    });

    return { status: 'success', taskId: task_id };
  }

  async linkInfoToTask(params: { task_id: string; info_node: string }): Promise<{ status: string }> {
    const { task_id, info_node } = params;

    await this.db.commit({
      triplets: [{ subject: task_id, relation: 'CONTAINS_INFO', object: info_node }]
    });

    return { status: 'success' };
  }

  setSessionId(sessionId: string): void {
    this.db.setSessionId(sessionId);
  }

  getSessionId(): string {
    return this.db.getSessionId();
  }
}
