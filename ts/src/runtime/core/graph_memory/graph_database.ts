import initSqlJs, { type Database as SqlJsDatabase } from 'sql.js';
import type { Platform } from 'waterflow/platform/types';
import type { Entity, Relation, RecallParams, CommitParams, PurgeParams, RecallResult, CommitResult, PurgeResult, MemoryStats } from './types';
import { getConfig } from './config';

export class GraphDatabase {
  private db: SqlJsDatabase | null = null;
  private sessionId: string;
  private initPromise: Promise<void> | null = null;
  private _platform: Platform | null = null;

  constructor(sessionId?: string) {
    this.sessionId = sessionId || `session-${Date.now()}`;
    this.initPromise = this.initDatabase();
  }

  private async initDatabase(): Promise<void> {
    const SQL = await initSqlJs();
    const { getPlatform } = await import('waterflow/platform');
    this._platform = getPlatform();

    try {
      const dbPath = this._platform.path.join(this._platform.getCwd(), getConfig().dbPath);
      const fs = this._platform.fs;
      if (fs) {
        const exists = await fs.exists(dbPath);
        if (exists) {
          const data = await fs.readFile(dbPath, { encoding: 'binary' });
          this.db = new SQL.Database(new Uint8Array(data as ArrayBuffer));
        } else {
          this.db = new SQL.Database();
        }
      } else {
        this.db = new SQL.Database();
      }
    } catch {
      this.db = new SQL.Database();
    }

    this.createTables();
  }

  async save(): Promise<void> {
    if (!this.db || !this._platform) return;

    try {
      const platform = this._platform;
      const fs = platform.fs;
      if (!fs) return;
      const dbPath = platform.path.join(platform.getCwd(), getConfig().dbPath);
      const dir = platform.path.dirname(dbPath);
      const dirExists = await fs.exists(dir);
      if (!dirExists) {
        await fs.mkdir(dir, true);
      }
      const data = this.db.export();
      await fs.writeFile(dbPath, data.buffer as ArrayBuffer, { encoding: 'binary' });
    } catch (error) {
      console.error(`[GraphDatabase] Save failed: ${error}`);
    }
  }

  private createTables(): void {
    if (!this.db) return;
    this.db.run(`
      CREATE TABLE IF NOT EXISTS entities (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        type TEXT DEFAULT 'unknown',
        mention_count INTEGER DEFAULT 1,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
      )
    `);
    this.db.run(`
      CREATE TABLE IF NOT EXISTS relations (
        id TEXT PRIMARY KEY,
        source_id TEXT NOT NULL,
        target_id TEXT NOT NULL,
        relation_type TEXT NOT NULL,
        confidence REAL DEFAULT 1.0,
        status TEXT DEFAULT 'active',
        session_id TEXT NOT NULL,
        turn_id INTEGER DEFAULT 0,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        date_bucket TEXT NOT NULL,
        FOREIGN KEY (source_id) REFERENCES entities(id),
        FOREIGN KEY (target_id) REFERENCES entities(id)
      )
    `);
    this.db.run(`CREATE INDEX IF NOT EXISTS idx_entity_name ON entities(name)`);
    this.db.run(`CREATE INDEX IF NOT EXISTS idx_entity_type ON entities(type)`);
    this.db.run(`CREATE INDEX IF NOT EXISTS idx_relation_source ON relations(source_id)`);
    this.db.run(`CREATE INDEX IF NOT EXISTS idx_relation_target ON relations(target_id)`);
    this.db.run(`CREATE INDEX IF NOT EXISTS idx_relation_type ON relations(relation_type)`);
    this.db.run(`CREATE INDEX IF NOT EXISTS idx_relation_status ON relations(status)`);
  }

  private ensureInit(): void {
    if (!this.db) {
      throw new Error('Database not initialized');
    }
  }

  async recall(params: RecallParams): Promise<RecallResult> {
    await this.initPromise;
    this.ensureInit();
    const { queryIntent, seedEntities, depth = 2, sessionFilter } = params;
    const keywords = queryIntent.split(/[,\s]+/).filter(k => k.length > 0);
    const entities: Entity[] = [];
    const relations: Relation[] = [];
    const entityIds = new Set<string>();

    if (!this.db) return { entities, relations, message: 'Database not ready' };

    if (!keywords.length && !seedEntities?.length) {
      const rows = this.db.exec('SELECT * FROM entities ORDER BY mention_count DESC LIMIT 50');
      if (rows.length > 0) {
        const columns = rows[0].columns;
        for (const row of rows[0].values) {
          const obj = this.rowToObject(columns, row);
          const id = obj.id as string;
          entityIds.add(id);
          entities.push(this.rowToEntity(obj, 0));
        }
      }
    } else {
      for (const keyword of keywords) {
        const stmt = this.db.prepare('SELECT * FROM entities WHERE LOWER(name) LIKE ? LIMIT 100');
        stmt.bind([`%${keyword.toLowerCase()}%`]);
        while (stmt.step()) {
          const row = stmt.getAsObject();
          const id = row.id as string;
          if (!entityIds.has(id)) {
            entityIds.add(id);
            entities.push(this.rowToEntity(row, 0));
          }
        }
        stmt.free();
      }
    }

    if (seedEntities?.length) {
      for (const seedName of seedEntities) {
        const stmt = this.db.prepare('SELECT * FROM entities WHERE LOWER(name) = ? LIMIT 1');
        stmt.bind([seedName.toLowerCase()]);
        if (stmt.step()) {
          const row = stmt.getAsObject();
          const id = row.id as string;
          if (!entityIds.has(id)) {
            entityIds.add(id);
            entities.push(this.rowToEntity(row, 0));
          }
        }
        stmt.free();
      }
    }

    this.bfsExpand(entityIds, entities, relations, depth, sessionFilter);

    for (const entity of entities) {
      if (entity.depth === undefined) {
        entity.depth = 0;
      }
    }

    return {
      entities,
      relations,
      message: `找到 ${entities.length} 个实体, ${relations.length} 条关系`
    };
  }

  private bfsExpand(
    seedIds: Set<string>,
    entities: Entity[],
    relations: Relation[],
    maxDepth: number,
    sessionFilter?: string
  ): void {
    if (!this.db) return;

    const visited = new Set(seedIds);
    let currentLayer = new Set(seedIds);
    const entityDepths: Record<string, number> = {};
    for (const id of seedIds) {
      entityDepths[id] = 0;
    }

    for (let layer = 0; layer < maxDepth; layer++) {
      if (!currentLayer.size) break;

      const placeholders = Array(currentLayer.size).fill('?').join(',');
      let sql = `
        SELECT r.id, r.source_id, r.target_id,
               e1.name as source_name, e2.name as target_name,
               r.relation_type, r.confidence, r.session_id,
               r.turn_id, r.created_at, r.updated_at, r.status, r.date_bucket
        FROM relations r
        JOIN entities e1 ON r.source_id = e1.id
        JOIN entities e2 ON r.target_id = e2.id
        WHERE (r.source_id IN (${placeholders}) OR r.target_id IN (${placeholders}))
          AND r.status = 'active'
      `;
      const params: (string | number)[] = [];
      for (const id of currentLayer) { params.push(id); }
      for (const id of currentLayer) { params.push(id); }
      if (sessionFilter) {
        sql += ` AND r.session_id = ?`;
        params.push(sessionFilter);
      }

      const stmt = this.db.prepare(sql);
      stmt.bind(params);

      const nextLayer = new Set<string>();
      const layerRelations: Relation[] = [];

      while (stmt.step()) {
        const row = stmt.getAsObject();
        const sourceId = row.source_id as string;
        const targetId = row.target_id as string;
        const sourceDepth = entityDepths[sourceId] ?? layer;
        const targetDepth = entityDepths[targetId] ?? layer;
        const relationDepth = Math.max(sourceDepth, targetDepth) + 1;

        layerRelations.push({
          id: row.id as string,
          sourceId,
          targetId,
          relationType: row.relation_type as string,
          confidence: row.confidence as number,
          status: row.status as Relation['status'],
          sessionId: row.session_id as string,
          turnId: row.turn_id as number,
          createdAt: new Date(row.created_at as string),
          updatedAt: new Date(row.updated_at as string),
          dateBucket: row.date_bucket as string,
          depth: relationDepth
        });

        if (!visited.has(sourceId)) {
          visited.add(sourceId);
          nextLayer.add(sourceId);
          entityDepths[sourceId] = layer + 1;
        }
        if (!visited.has(targetId)) {
          visited.add(targetId);
          nextLayer.add(targetId);
          entityDepths[targetId] = layer + 1;
        }
      }
      stmt.free();

      relations.push(...layerRelations);

      if (nextLayer.size) {
        const placeholders = Array(nextLayer.size).fill('?').join(',');
        const entityStmt = this.db.prepare(
          `SELECT * FROM entities WHERE id IN (${placeholders})`
        );
        entityStmt.bind(Array.from(nextLayer));
        while (entityStmt.step()) {
          const row = entityStmt.getAsObject();
          const id = row.id as string;
          entities.push(this.rowToEntity(row, entityDepths[id] ?? layer + 1));
        }
        entityStmt.free();
      }

      currentLayer = nextLayer;
    }
  }

  async commit(params: CommitParams): Promise<CommitResult> {
    await this.initPromise;
    this.ensureInit();
    const { triplets, sessionId, turnId } = params;
    let createdEntities = 0;
    let createdRelations = 0;

    if (!this.db) return { createdEntities: 0, createdRelations: 0 };

    for (const triplet of triplets) {
      const sourceId = this.upsertEntity(triplet.subject);
      const targetId = this.upsertEntity(triplet.object);

      const relationId = this.generateId();
      const now = new Date().toISOString();
      this.db.run(
        `INSERT INTO relations (id, source_id, target_id, relation_type, confidence, status, session_id, turn_id, created_at, updated_at, date_bucket)
         VALUES (?, ?, ?, ?, ?, 'active', ?, ?, ?, ?, ?)`,
        [relationId, sourceId, targetId, triplet.relation, triplet.confidence ?? 1.0, sessionId ?? this.sessionId, turnId ?? 0, now, now, new Date().toISOString().split('T')[0]]
      );

      createdEntities += 2;
      createdRelations++;
    }

    if (getConfig().autoSave) {
      await this.save();
    }

    return { createdEntities, createdRelations };
  }

  async purge(params: PurgeParams): Promise<PurgeResult> {
    await this.initPromise;
    this.ensureInit();
    const { criteria, mode = 'soft' } = params;
    let deleted = 0;

    if (!this.db) return { deleted: 0, mode };

    const conditions: string[] = [];
    const queryParams: (string | number)[] = [];

    if (criteria?.subject) {
      const stmt = this.db.prepare('SELECT id FROM entities WHERE LOWER(name) = ?');
      stmt.bind([criteria.subject.toLowerCase()]);
      if (stmt.step()) {
        const row = stmt.getAsObject();
        conditions.push(`source_id = ?`);
        queryParams.push(row.id as string);
      }
      stmt.free();
    }

    if (criteria?.target) {
      const stmt = this.db.prepare('SELECT id FROM entities WHERE LOWER(name) = ?');
      stmt.bind([criteria.target.toLowerCase()]);
      if (stmt.step()) {
        const row = stmt.getAsObject();
        conditions.push(`target_id = ?`);
        queryParams.push(row.id as string);
      }
      stmt.free();
    }

    if (criteria?.relation) {
      conditions.push(`relation_type = ?`);
      queryParams.push(criteria.relation);
    }

    if (!conditions.length) {
      return { deleted: 0, mode, message: '无删除条件' };
    }

    const whereClause = conditions.join(' AND ');

    const countStmt = this.db.prepare(`SELECT COUNT(*) as cnt FROM relations WHERE ${whereClause} AND status = 'active'`);
    countStmt.bind(queryParams);
    if (countStmt.step()) {
      const row = countStmt.getAsObject();
      deleted = row.cnt as number;
    }
    countStmt.free();

    if (mode === 'hard') {
      this.db.run(`DELETE FROM relations WHERE ${whereClause} AND status = 'active'`, queryParams);
    } else {
      this.db.run(
        `UPDATE relations SET status = 'deleted', updated_at = ? WHERE ${whereClause} AND status = 'active'`,
        [new Date().toISOString(), ...queryParams]
      );
    }

    if (getConfig().autoSave && deleted > 0) {
      await this.save();
    }

    return { deleted, mode };
  }

  async introspect(): Promise<MemoryStats> {
    await this.initPromise;
    this.ensureInit();

    if (!this.db) return { entityCount: 0, relationCount: 0, sessionId: this.sessionId };

    const entityCount = (this.db.exec('SELECT COUNT(*) FROM entities')[0]?.values[0]?.[0] as number) ?? 0;
    const relationCount = (this.db.exec("SELECT COUNT(*) FROM relations WHERE status = 'active'")[0]?.values[0]?.[0] as number) ?? 0;

    return { entityCount, relationCount, sessionId: this.sessionId };
  }

  private upsertEntity(name: string): string {
    if (!this.db) return this.generateId();

    const existingStmt = this.db.prepare('SELECT id, mention_count FROM entities WHERE LOWER(name) = ?');
    existingStmt.bind([name.toLowerCase()]);
    if (existingStmt.step()) {
      const row = existingStmt.getAsObject();
      const id = row.id as string;
      this.db.run('UPDATE entities SET mention_count = ?, updated_at = ? WHERE id = ?', [(row.mention_count as number) + 1, new Date().toISOString(), id]);
      existingStmt.free();
      return id;
    }
    existingStmt.free();

    const id = this.generateId();
    const now = new Date().toISOString();
    this.db.run(
      'INSERT INTO entities (id, name, type, mention_count, created_at, updated_at) VALUES (?, ?, ?, 1, ?, ?)',
      [id, name, 'unknown', now, now]
    );
    return id;
  }

  private rowToEntity(row: Record<string, unknown>, depth?: number): Entity {
    const entity: Entity = {
      id: row.id as string,
      name: row.name as string,
      type: (row.type as string) ?? 'unknown',
      mentionCount: row.mention_count as number,
      createdAt: new Date(row.created_at as string),
      updatedAt: new Date(row.updated_at as string)
    };
    if (depth !== undefined) {
      entity.depth = depth;
    }
    return entity;
  }

  private rowToObject(columns: string[], values: unknown[]): Record<string, unknown> {
    const obj: Record<string, unknown> = {};
    columns.forEach((col, i) => { obj[col] = values[i]; });
    return obj;
  }

  private generateId(): string {
    if (this._platform?.globals?.randomUUID) {
      return this._platform.globals.randomUUID();
    }
    return `ent-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
  }

  setSessionId(sessionId: string): void {
    this.sessionId = sessionId;
  }

  getSessionId(): string {
    return this.sessionId;
  }

  close(): void {
    if (this.db) {
      this.db.close();
      this.db = null;
    }
  }
}
