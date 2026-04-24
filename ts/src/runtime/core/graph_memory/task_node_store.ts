import Database from 'better-sqlite3';
import * as fs from 'fs';
import * as path from 'path';
import type { TaskNodeData } from './types.js';

export { TaskNodeData as TaskNode };

export class TaskNodeStore {
  private db: Database.Database;
  private archiveDir: string;

  constructor(dbPath?: string, archiveDir?: string) {
    this.db = new Database(dbPath || 'graph_memory.db');
    this.archiveDir = archiveDir || './task_archive';
    this.initialize();
  }

  private initialize(): void {
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS task_nodes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        turn_id INTEGER NOT NULL,
        summary TEXT NOT NULL,
        key_facts TEXT NOT NULL DEFAULT '[]',
        created_at TEXT DEFAULT (datetime('now'))
      )
    `);

    this.db.exec(`
      CREATE TABLE IF NOT EXISTS task_chains (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        from_node_id INTEGER NOT NULL,
        to_node_id INTEGER NOT NULL,
        relation_type TEXT DEFAULT 'next',
        created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (from_node_id) REFERENCES task_nodes(id),
        FOREIGN KEY (to_node_id) REFERENCES task_nodes(id)
      )
    `);

    this.db.exec(`
      CREATE INDEX IF NOT EXISTS idx_task_nodes_session ON task_nodes(session_id);
      CREATE INDEX IF NOT EXISTS idx_task_nodes_turn ON task_nodes(session_id, turn_id);
      CREATE INDEX IF NOT EXISTS idx_task_chains_session ON task_chains(session_id);
      CREATE INDEX IF NOT EXISTS idx_task_chains_from ON task_chains(from_node_id);
    `);

    if (!fs.existsSync(this.archiveDir)) {
      fs.mkdirSync(this.archiveDir, { recursive: true });
    }
  }

  async createTaskNode(params: {
    session_id: string;
    turn_id: number;
    summary: string;
    key_facts: string[];
    raw_context?: string | undefined;
  }): Promise<{ node_id: number; chain_linked: boolean }> {
    const { session_id, turn_id, summary, key_facts, raw_context } = params;

    const insert = this.db.prepare(`
      INSERT INTO task_nodes (session_id, turn_id, summary, key_facts)
      VALUES (?, ?, ?, ?)
    `);
    const result = insert.run(session_id, turn_id, summary, JSON.stringify(key_facts));
    const nodeId = Number(result.lastInsertRowid);

    // Link to previous node in chain
    let chainLinked = false;
    const prevNode = this.db.prepare(`
      SELECT id FROM task_nodes
      WHERE session_id = ? AND turn_id < ?
      ORDER BY turn_id DESC LIMIT 1
    `).get(session_id, turn_id) as { id: number } | undefined;

    if (prevNode) {
      this.db.prepare(`
        INSERT INTO task_chains (session_id, from_node_id, to_node_id, relation_type)
        VALUES (?, ?, ?, 'next')
      `).run(session_id, prevNode.id, nodeId);
      chainLinked = true;
    }

    // Archive raw context to text file if provided
    if (raw_context) {
      const archivePath = path.join(this.archiveDir, `${session_id}_turn${turn_id}.txt`);
      fs.writeFileSync(archivePath, raw_context, 'utf-8');
    }

    return { node_id: nodeId, chain_linked: chainLinked };
  }

  async getRecentTaskNodes(session_id: string, limit: number = 5): Promise<TaskNodeData[]> {
    const rows = this.db.prepare(`
      SELECT * FROM task_nodes
      WHERE session_id = ?
      ORDER BY turn_id DESC
      LIMIT ?
    `).all(session_id, limit) as Array<Record<string, unknown>>;

    return rows.map(r => ({
      id: r.id as number,
      session_id: r.session_id as string,
      turn_id: r.turn_id as number,
      summary: r.summary as string,
      key_facts: r.key_facts as string,
      created_at: r.created_at as string
    })).reverse(); // Return in chronological order
  }

  async getTaskChain(session_id: string, from_node_id?: number): Promise<{
    nodes: TaskNodeData[];
    relations: Array<{ from: number; to: number; type: string }>;
  }> {
    let startNode = from_node_id;
    if (!startNode) {
      const latest = this.db.prepare(`
        SELECT id FROM task_nodes WHERE session_id = ? ORDER BY turn_id DESC LIMIT 1
      `).get(session_id) as { id: number } | undefined;
      if (!latest) return { nodes: [], relations: [] };
      startNode = latest.id;
    }

    // Walk backwards through the chain
    const nodes: TaskNodeData[] = [];
    const relations: Array<{ from: number; to: number; type: string }> = [];
    const visited = new Set<number>();
    let current = startNode;

    while (current && !visited.has(current)) {
      visited.add(current);
      const node = this.db.prepare(`SELECT * FROM task_nodes WHERE id = ?`).get(current) as Record<string, unknown> | undefined;
      if (node) {
        nodes.unshift({
          id: node.id as number,
          session_id: node.session_id as string,
          turn_id: node.turn_id as number,
          summary: node.summary as string,
          key_facts: node.key_facts as string,
          created_at: node.created_at as string
        });
      }

      const prevChain = this.db.prepare(`
        SELECT from_node_id, relation_type FROM task_chains WHERE to_node_id = ? AND session_id = ?
      `).get(current, session_id) as { from_node_id: number; relation_type: string } | undefined;

      if (prevChain) {
        relations.unshift({
          from: prevChain.from_node_id,
          to: current,
          type: prevChain.relation_type
        });
        current = prevChain.from_node_id;
      } else {
        break;
      }
    }

    return { nodes, relations };
  }

  async archiveRawContext(session_id: string, turn_id: number, raw_context: string): Promise<string> {
    const archivePath = path.join(this.archiveDir, `${session_id}_turn${turn_id}.txt`);
    fs.writeFileSync(archivePath, raw_context, 'utf-8');
    return archivePath;
  }

  async readArchivedContext(session_id: string, turn_id: number): Promise<string | null> {
    const archivePath = path.join(this.archiveDir, `${session_id}_turn${turn_id}.txt`);
    if (fs.existsSync(archivePath)) {
      return fs.readFileSync(archivePath, 'utf-8');
    }
    return null;
  }

  close(): void {
    this.db.close();
  }
}
