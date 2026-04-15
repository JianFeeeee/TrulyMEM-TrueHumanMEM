import type { Entity, Relation, RecallParams, CommitParams, PurgeParams, RecallResult, CommitResult, PurgeResult, MemoryStats } from './types';

export class GraphDatabase {
  private entities: Map<string, Entity> = new Map();
  private relations: Map<string, Relation> = new Map();
  private sessionId: string;

  constructor(sessionId?: string) {
    this.sessionId = sessionId || `session-${Date.now()}`;
  }

  async recall(params: RecallParams): Promise<RecallResult> {
    const { queryIntent, seedEntities, sessionFilter } = params;
    const keywords = queryIntent.split(/[,\s]+/).filter(k => k.length > 0);
    const entities: Entity[] = [];
    const relations: Relation[] = [];
    const entityIds = new Set<string>();

    for (const keyword of keywords) {
      const lowerKeyword = keyword.toLowerCase();
      for (const [_, entity] of this.entities) {
        if (entity.name.toLowerCase().includes(lowerKeyword)) {
          if (!entityIds.has(entity.id)) {
            entityIds.add(entity.id);
            entities.push(entity);
          }
        }
      }
    }

    if (seedEntities && seedEntities.length > 0) {
      for (const seedName of seedEntities) {
        for (const [_, entity] of this.entities) {
          if (entity.name.toLowerCase() === seedName.toLowerCase()) {
            if (!entityIds.has(entity.id)) {
              entityIds.add(entity.id);
              entities.push(entity);
            }
          }
        }
      }
    }

    for (const [_, relation] of this.relations) {
      if (entityIds.has(relation.sourceId) || entityIds.has(relation.targetId)) {
        if (relation.status === 'active') {
          if (!sessionFilter || relation.sessionId === sessionFilter) {
            relations.push(relation);
          }
        }
      }
    }

    return {
      entities,
      relations,
      message: `找到 ${entities.length} 个实体, ${relations.length} 条关系`
    };
  }

  async commit(params: CommitParams): Promise<CommitResult> {
    const { triplets, sessionId, turnId } = params;
    let createdEntities = 0;
    let createdRelations = 0;

    for (const triplet of triplets) {
      const sourceId = this.upsertEntity(triplet.subject);
      const targetId = this.upsertEntity(triplet.object);

      const relationId = this.generateId();
      const now = new Date();
      const relation: Relation = {
        id: relationId,
        sourceId,
        targetId,
        relationType: triplet.relation,
        confidence: triplet.confidence || 1.0,
        status: 'active',
        sessionId: sessionId || this.sessionId,
        turnId: turnId || 0,
        createdAt: now,
        updatedAt: now,
        dateBucket: this.getDateBucket(now)
      };

      this.relations.set(relationId, relation);
      createdEntities += 2;
      createdRelations++;
    }

    return { createdEntities, createdRelations };
  }

  async purge(params: PurgeParams): Promise<PurgeResult> {
    const { criteria, mode = 'soft' } = params;
    let deleted = 0;

    for (const [id, relation] of this.relations) {
      if (relation.status !== 'active') continue;

      if (!criteria) {
        continue;
      }

      let matches = true;
      if (criteria.subject) {
        const sourceEntity = this.entities.get(relation.sourceId);
        matches = sourceEntity?.name.toLowerCase() === criteria.subject.toLowerCase();
      }
      if (matches && criteria.target) {
        const targetEntity = this.entities.get(relation.targetId);
        matches = targetEntity?.name.toLowerCase() === criteria.target.toLowerCase();
      }
      if (matches && criteria.relation) {
        matches = relation.relationType.toLowerCase() === criteria.relation.toLowerCase();
      }
      if (matches && criteria.sessionId) {
        matches = relation.sessionId === criteria.sessionId;
      }

      if (matches) {
        if (mode === 'hard') {
          this.relations.delete(id);
        } else {
          relation.status = 'deleted';
          relation.updatedAt = new Date();
        }
        deleted++;
      }
    }

    return { deleted, mode };
  }

  async introspect(): Promise<MemoryStats> {
    let entityCount = 0;
    for (const [_, entity] of this.entities) {
      if (!this.isEntityDeleted(entity.id)) entityCount++;
    }

    let relationCount = 0;
    for (const [_, relation] of this.relations) {
      if (relation.status === 'active') relationCount++;
    }

    return { entityCount, relationCount, sessionId: this.sessionId };
  }

  private upsertEntity(name: string): string {
    for (const [id, entity] of this.entities) {
      if (entity.name === name && !this.isEntityDeleted(id)) {
        entity.mentionCount++;
        entity.updatedAt = new Date();
        return id;
      }
    }

    const id = this.generateId();
    const now = new Date();
    const entity: Entity = {
      id,
      name,
      type: 'unknown',
      mentionCount: 1,
      createdAt: now,
      updatedAt: now
    };
    this.entities.set(id, entity);
    return id;
  }

  private isEntityDeleted(entityId: string): boolean {
    for (const [_, relation] of this.relations) {
      if ((relation.sourceId === entityId || relation.targetId === entityId) && relation.status === 'deleted') {
        return true;
      }
    }
    return false;
  }

  private generateId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  private getDateBucket(date: Date): string {
    return date.toISOString().split('T')[0] ?? '';
  }

  setSessionId(sessionId: string): void {
    this.sessionId = sessionId;
  }

  getSessionId(): string {
    return this.sessionId;
  }
}
