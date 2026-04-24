import Database from 'better-sqlite3';
import type {
  Entity, Relation, RecallParams, CommitParams, PurgeParams,
  RecallResult, CommitResult, PurgeResult, MemoryStats
} from './types.js';

export class GraphDatabase {
  private db: Database.Database;
  private sessionId: string;

  constructor(dbPath?: string, sessionId?: string) {
    this.db = new Database(dbPath || 'graph_memory.db');
    this.sessionId = sessionId || `session-${Date.now()}`;
    this.db.pragma('journal_mode = WAL');
    this.initialize();
  }

  private initialize(): void {
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS entities (
        id TEXT PRIMARY KEY,
        name TEXT UNIQUE NOT NULL,
        type TEXT DEFAULT 'unknown',
        mention_count INTEGER DEFAULT 1,
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now'))
      )
    `);

    this.db.exec(`
      CREATE TABLE IF NOT EXISTS relations (
        id TEXT PRIMARY KEY,
        source_id TEXT NOT NULL,
        target_id TEXT NOT NULL,
        relation_type TEXT NOT NULL,
        confidence REAL DEFAULT 1.0,
        status TEXT DEFAULT 'active',
        session_id TEXT,
        turn_id INTEGER DEFAULT 0,
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now')),
        date_bucket TEXT,
        superseded_by TEXT,
        FOREIGN KEY (source_id) REFERENCES entities(id),
        FOREIGN KEY (target_id) REFERENCES entities(id)
      )
    `);

    this.db.exec(`
      CREATE INDEX IF NOT EXISTS idx_entity_name ON entities(name);
      CREATE INDEX IF NOT EXISTS idx_entity_type ON entities(type);
      CREATE INDEX IF NOT EXISTS idx_relation_source ON relations(source_id);
      CREATE INDEX IF NOT EXISTS idx_relation_target ON relations(target_id);
      CREATE INDEX IF NOT EXISTS idx_relation_type ON relations(relation_type);
      CREATE INDEX IF NOT EXISTS idx_relation_status ON relations(status);
      CREATE INDEX IF NOT EXISTS idx_relation_session ON relations(session_id);
      CREATE INDEX IF NOT EXISTS idx_relation_date ON relations(date_bucket);
      CREATE INDEX IF NOT EXISTS idx_relation_superseded ON relations(superseded_by);
    `);
  }

  async recall(params: RecallParams): Promise<RecallResult> {
    const { queryIntent, seedEntities, depth = 2, timeRange, sessionFilter } = params;
    const keywords = queryIntent.split(/[,\s]+/).filter(k => k.length > 0);
    const entityIds = new Set<string>();
    const entities: Entity[] = [];
    const relations: Relation[] = [];

    if (keywords.length === 0 && (!seedEntities || seedEntities.length === 0)) {
      return { entities: [], relations: [], message: 'No query keywords' };
    }

    const timeCondition = timeRange?.days
      ? `AND r.created_at >= datetime('now', '-${timeRange.days} days')`
      : '';
    const sessionCondition = sessionFilter ? `AND r.session_id = ?` : '';

    if (keywords.length > 0) {
      const likeConditions = keywords.map(() => `LOWER(e.name) LIKE ?`).join(' OR ');
      const likeParams = keywords.map(k => `%${k.toLowerCase()}%`);
      const seedRows = this.db.prepare(
        `SELECT DISTINCT e.* FROM entities e WHERE ${likeConditions}`
      ).all(...likeParams) as Array<Record<string, unknown>>;

      for (const row of seedRows) {
        const id = row.id as string;
        if (!entityIds.has(id)) {
          entityIds.add(id);
          entities.push(this.rowToEntity(row));
        }
      }
    }

    if (seedEntities && seedEntities.length > 0) {
      const placeholders = seedEntities.map(() => '?').join(',');
      const exactRows = this.db.prepare(
        `SELECT * FROM entities WHERE LOWER(name) IN (${placeholders})`
      ).all(...seedEntities.map(s => s.toLowerCase())) as Array<Record<string, unknown>>;

      for (const row of exactRows) {
        const id = row.id as string;
        if (!entityIds.has(id)) {
          entityIds.add(id);
          entities.push(this.rowToEntity(row));
        }
      }
    }

    const visited = new Set<string>(entityIds);
    let currentLevel = new Set<string>(entityIds);

    for (let d = 1; d < depth; d++) {
      const nextLevel = new Set<string>();
      const idsArray = Array.from(currentLevel);
      if (idsArray.length === 0) break;

      const placeholders = idsArray.map(() => '?').join(',');
      const neighborRows = this.db.prepare(`
        SELECT DISTINCT e.* FROM entities e
        JOIN relations r ON (r.source_id = e.id OR r.target_id = e.id)
        WHERE (r.source_id IN (${placeholders}) OR r.target_id IN (${placeholders}))
          AND r.status = 'active'
          ${timeCondition}
          ${sessionCondition}
        LIMIT 200
      `).all(...idsArray, ...idsArray, ...(sessionFilter ? [sessionFilter] : [])) as Array<Record<string, unknown>>;

      for (const row of neighborRows) {
        const id = row.id as string;
        if (!visited.has(id)) {
          visited.add(id);
          nextLevel.add(id);
          entities.push(this.rowToEntity(row));
        }
      }
      currentLevel = nextLevel;
    }

    if (entityIds.size > 0) {
      const allIds = Array.from(entityIds);
      const placeholders = allIds.map(() => '?').join(',');
      const relationRows = this.db.prepare(`
        SELECT r.*, e1.name as source_name, e2.name as target_name
        FROM relations r
        JOIN entities e1 ON r.source_id = e1.id
        JOIN entities e2 ON r.target_id = e2.id
        WHERE (r.source_id IN (${placeholders}) OR r.target_id IN (${placeholders}))
          AND r.status = 'active'
          ${timeCondition}
          ${sessionCondition}
        ORDER BY r.created_at DESC
        LIMIT 100
      `).all(...allIds, ...allIds, ...(sessionFilter ? [sessionFilter] : [])) as Array<Record<string, unknown>>;

      for (const row of relationRows) {
        relations.push(this.rowToRelation(row));
      }
    }

    return { entities, relations, message: `Found ${entities.length} entities, ${relations.length} relations` };
  }

  async commit(params: CommitParams): Promise<CommitResult> {
    const { triplets, sessionId, turnId } = params;
    let createdEntities = 0;
    let createdRelations = 0;

    const insertRelation = this.db.prepare(`
      INSERT INTO relations (id, source_id, target_id, relation_type, confidence, session_id, turn_id, status, date_bucket)
      VALUES (?, ?, ?, ?, ?, ?, ?, 'active', ?)
    `);

    const insertEntity = this.db.prepare(`
      INSERT OR IGNORE INTO entities (id, name, type) VALUES (?, ?, 'unknown')
    `);

    const updateEntity = this.db.prepare(`
      UPDATE entities SET mention_count = mention_count + 1, updated_at = datetime('now') WHERE name = ?
    `);

    const getEntity = this.db.prepare(`SELECT id FROM entities WHERE name = ?`);

    for (const triplet of triplets) {
      const dateBucket = new Date().toISOString().split('T')[0] ?? '';

      let sourceId = (getEntity.get(triplet.subject) as { id: string } | undefined)?.id;
      if (sourceId) {
        updateEntity.run(triplet.subject);
      } else {
        sourceId = this.generateId();
        insertEntity.run(sourceId, triplet.subject);
      }
      createdEntities++;

      let targetId = (getEntity.get(triplet.object) as { id: string } | undefined)?.id;
      if (targetId) {
        updateEntity.run(triplet.object);
      } else {
        targetId = this.generateId();
        insertEntity.run(targetId, triplet.object);
      }
      createdEntities++;

      insertRelation.run(
        this.generateId(), sourceId, targetId, triplet.relation,
        triplet.confidence || 1.0, sessionId || this.sessionId,
        turnId || 0, dateBucket
      );
      createdRelations++;
    }

    return { createdEntities, createdRelations };
  }

  async purge(params: PurgeParams): Promise<PurgeResult> {
    const { criteria, mode = 'soft', newRelation } = params;
    let deleted = 0;
    if (!criteria) return { deleted: 0, mode };

    const conditions: string[] = ["status = 'active'"];
    const values: unknown[] = [];

    if (criteria.subject) {
      conditions.push(`source_id IN (SELECT id FROM entities WHERE LOWER(name) = ?)`);
      values.push(criteria.subject.toLowerCase());
    }
    if (criteria.target) {
      conditions.push(`target_id IN (SELECT id FROM entities WHERE LOWER(name) = ?)`);
      values.push(criteria.target.toLowerCase());
    }
    if (criteria.relation) {
      conditions.push(`LOWER(relation_type) = ?`);
      values.push(criteria.relation.toLowerCase());
    }
    if (criteria.sessionId) {
      conditions.push(`session_id = ?`);
      values.push(criteria.sessionId);
    }

    const whereClause = conditions.join(' AND ');

    if (mode === 'supersede' && newRelation) {
      const ids = this.db.prepare(
        `SELECT id, source_id, target_id FROM relations WHERE ${whereClause}`
      ).all(...values) as Array<{ id: string; source_id: string; target_id: string }>;

      for (const row of ids) {
        const newId = this.generateId();
        this.db.prepare(`
          INSERT INTO relations (id, source_id, target_id, relation_type, confidence, session_id, turn_id, status, date_bucket, superseded_by)
          VALUES (?, ?, ?, ?, 1.0, ?, 0, 'active', ?, ?)
        `).run(newId, row.source_id, row.target_id, newRelation.relation, this.sessionId, new Date().toISOString().split('T')[0], row.id);

        this.db.prepare(`
          UPDATE relations SET status = 'superseded', superseded_by = ?, updated_at = datetime('now') WHERE id = ?
        `).run(newId, row.id);
        deleted++;
      }
    } else if (mode === 'hard') {
      const result = this.db.prepare(`DELETE FROM relations WHERE ${whereClause}`).run(...values);
      deleted = result.changes;
    } else {
      const result = this.db.prepare(`UPDATE relations SET status = 'deleted', updated_at = datetime('now') WHERE ${whereClause}`).run(...values);
      deleted = result.changes;
    }

    return { deleted, mode };
  }

  async introspect(): Promise<MemoryStats> {
    const entityCount = (this.db.prepare(`SELECT COUNT(*) as c FROM entities`).get() as { c: number }).c;
    const relationCount = (this.db.prepare(`SELECT COUNT(*) as c FROM relations WHERE status = 'active'`).get() as { c: number }).c;
    return { entityCount, relationCount, sessionId: this.sessionId };
  }

  async archive(days: number = 30): Promise<{ archived: number }> {
    const result = this.db.prepare(`
      UPDATE relations SET status = 'archived', updated_at = datetime('now')
      WHERE status = 'active' AND created_at < datetime('now', '-' || ? || ' days')
    `).run(days);
    return { archived: result.changes };
  }

  async cleanup(dryRun: boolean = true): Promise<{ deleted_relations: number; deleted_entities: number; details?: string[] }> {
    const details: string[] = [];
    const oldRelations = this.db.prepare(`
      SELECT id FROM relations WHERE status = 'deleted' AND updated_at < datetime('now', '-90 days')
    `).all() as Array<{ id: string }>;

    if (dryRun) {
      details.push(`Will delete ${oldRelations.length} old deleted relations`);
      const orphaned = this.db.prepare(`
        SELECT e.id, e.name FROM entities e
        WHERE e.id NOT IN (SELECT DISTINCT source_id FROM relations WHERE status != 'deleted')
          AND e.id NOT IN (SELECT DISTINCT target_id FROM relations WHERE status != 'deleted')
      `).all() as Array<{ id: string; name: string }>;
      details.push(`Will delete ${orphaned.length} orphaned entities`);
      return { deleted_relations: oldRelations.length, deleted_entities: orphaned.length, details };
    }

    const deleteResult = this.db.prepare(`
      DELETE FROM relations WHERE status = 'deleted' AND updated_at < datetime('now', '-90 days')
    `).run();

    const deleteOrphans = this.db.prepare(`
      DELETE FROM entities
      WHERE id NOT IN (SELECT DISTINCT source_id FROM relations)
        AND id NOT IN (SELECT DISTINCT target_id FROM relations)
    `).run();

    return { deleted_relations: deleteResult.changes, deleted_entities: deleteOrphans.changes };
  }

  private rowToEntity(row: Record<string, unknown>): Entity {
    return {
      id: row.id as string, name: row.name as string,
      type: (row.type as string) || 'unknown', mentionCount: (row.mention_count as number) || 1,
      createdAt: new Date(row.created_at as string), updatedAt: new Date(row.updated_at as string)
    };
  }

  private rowToRelation(row: Record<string, unknown>): Relation {
    return {
      id: row.id as string, sourceId: row.source_id as string, targetId: row.target_id as string,
      relationType: row.relation_type as string, confidence: (row.confidence as number) || 1.0,
      status: (row.status as Relation['status']) || 'active',
      sessionId: (row.session_id as string) || this.sessionId,
      turnId: (row.turn_id as number) || 0,
      createdAt: new Date(row.created_at as string), updatedAt: new Date(row.updated_at as string),
      dateBucket: (row.date_bucket as string) || ''
    };
  }

  private generateId(): string {
    return `${Date.now()}-${Math.random().toString(36).substring(2, 11)}`;
  }

  setSessionId(sessionId: string): void { this.sessionId = sessionId; }
  getSessionId(): string { return this.sessionId; }
  close(): void { this.db.close(); }
}
