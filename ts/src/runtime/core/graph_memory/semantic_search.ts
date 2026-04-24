import Database from 'better-sqlite3';

export interface SemanticMemory {
  id: string;
  text: string;
  embedding: Float32Array;
  source: string;
  sourceLine?: number;
  createdAt: Date;
}

export interface SearchResult {
  id: string;
  text: string;
  source: string;
  sourceLine?: number;
  similarity: number;
}

export class SemanticSearchEngine {
  private db: Database.Database;
  private embeddingModel: any;
  private modelReady: boolean = false;

  constructor(db: Database.Database) {
    this.db = db;
    this.initialize();
  }

  private initialize(): void {
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS embeddings (
        id TEXT PRIMARY KEY,
        text TEXT NOT NULL,
        embedding BLOB NOT NULL,
        source TEXT,
        source_line INTEGER,
        created_at TEXT DEFAULT (datetime('now'))
      );
      CREATE INDEX IF NOT EXISTS idx_embeddings_source ON embeddings(source);
    `);
  }

  async loadModel(): Promise<void> {
    if (this.modelReady) return;
    const { pipeline } = await import('@xenova/transformers') as any;
    this.embeddingModel = await pipeline('feature-extraction', 'Xenova/all-MiniLM-L6-v2');
    this.modelReady = true;
  }

  async generateEmbedding(text: string): Promise<Float32Array> {
    await this.loadModel();
    const output = await this.embeddingModel(text, { pooling: 'mean', normalize: true });
    return new Float32Array(output.data);
  }

  storeEmbedding(id: string, text: string, embedding: Float32Array, source?: string, sourceLine?: number): void {
    const stmt = this.db.prepare(`
      INSERT OR REPLACE INTO embeddings (id, text, embedding, source, source_line)
      VALUES (?, ?, ?, ?, ?)
    `);
    stmt.run(id, text, Buffer.from(embedding.buffer), source || null, sourceLine || null);
  }

  searchSimilar(queryEmbedding: Float32Array, limit: number = 10): SearchResult[] {
    const rows = this.db.prepare('SELECT id, text, embedding, source, source_line FROM embeddings').all();
    const results = rows.map((row: any) => ({
      id: row.id,
      text: row.text,
      source: row.source,
      sourceLine: row.source_line,
      similarity: cosineSimilarity(queryEmbedding, new Float32Array(row.embedding.buffer))
    }));
    return results.sort((a: SearchResult, b: SearchResult) => b.similarity - a.similarity).slice(0, limit);
  }
}

export function cosineSimilarity(a: Float32Array, b: Float32Array): number {
  let dot = 0, normA = 0, normB = 0;
  for (let i = 0; i < a.length; i++) {
    dot += a[i] * b[i];
    normA += a[i] * a[i];
    normB += b[i] * b[i];
  }
  return dot / (Math.sqrt(normA) * Math.sqrt(normB));
}
