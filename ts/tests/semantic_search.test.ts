import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import Database from 'better-sqlite3';

vi.mock('@xenova/transformers', () => ({
  pipeline: vi.fn().mockImplementation(() => {
    const mockModel = (text: string, opts: any) => {
      const arr = new Float32Array(384);
      const seed = text.split('').reduce((a, c) => a + c.charCodeAt(0), 0);
      for (let i = 0; i < 384; i++) {
        arr[i] = Math.sin((seed + i) * 0.1);
      }
      return { data: arr };
    };
    mockModel.to = function() {
      return this;
    };
    return mockModel;
  }),
}));

import { SemanticSearchEngine, cosineSimilarity } from '/home/program/TrulyMEM-TrueHumanMEM/ts/dist/runtime/core/graph_memory/semantic_search.js';

const TEST_DB_PATH = '/tmp/test_semantic_search.db';

describe('SemanticSearchEngine', () => {
  let db: Database.Database;
  let engine: SemanticSearchEngine;

  beforeEach(async () => {
    try {
      const fs = await import('fs');
      if (fs.existsSync(TEST_DB_PATH)) {
        fs.unlinkSync(TEST_DB_PATH);
      }
      if (fs.existsSync(`${TEST_DB_PATH}-wal`)) {
        fs.unlinkSync(`${TEST_DB_PATH}-wal`);
      }
      if (fs.existsSync(`${TEST_DB_PATH}-shm`)) {
        fs.unlinkSync(`${TEST_DB_PATH}-shm`);
      }
    } catch {}
    db = new Database(TEST_DB_PATH);
    engine = new SemanticSearchEngine(db);
  });

  afterEach(() => {
    if (db) {
      db.close();
    }
  });

  describe('initialization', () => {
    it('creates embeddings table on initialization', () => {
      const tableInfo = db.prepare("SELECT name FROM sqlite_master WHERE type='table' AND name='embeddings'").get();
      expect(tableInfo).toBeDefined();
    });

    it('creates index on source column', () => {
      const indexInfo = db.prepare("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_embeddings_source'").get();
      expect(indexInfo).toBeDefined();
    });
  });

  describe('generateEmbedding', () => {
    it('generates 384 dimensional embedding', async () => {
      const embedding = await engine.generateEmbedding('hello world');
      expect(embedding.length).toBe(384);
    });

    it('generates consistent embeddings for same text', async () => {
      const emb1 = await engine.generateEmbedding('test');
      const emb2 = await engine.generateEmbedding('test');
      expect(emb1.length).toBe(emb2.length);
      const similarity = cosineSimilarity(emb1, emb2);
      expect(similarity).toBeCloseTo(1, 3);
    });

    it('generates different embeddings for different text', async () => {
      const emb1 = await engine.generateEmbedding('hello');
      const emb2 = await engine.generateEmbedding('world');
      const similarity = cosineSimilarity(emb1, emb2);
      expect(similarity).not.toBe(1);
    });
  });

  describe('storeEmbedding', () => {
    it('stores embedding to SQLite', async () => {
      const embedding = await engine.generateEmbedding('test');
      engine.storeEmbedding('test-id', 'test text', embedding, 'test-source', 1);

      const row = db.prepare('SELECT * FROM embeddings WHERE id = ?').get('test-id') as any;
      expect(row).toBeDefined();
      expect(row.text).toBe('test text');
      expect(row.source).toBe('test-source');
      expect(row.source_line).toBe(1);
    });

    it('replaces existing embedding with same id', async () => {
      const emb1 = await engine.generateEmbedding('text1');
      engine.storeEmbedding('dup-id', 'text 1', emb1);

      const emb2 = await engine.generateEmbedding('text2');
      engine.storeEmbedding('dup-id', 'text 2', emb2);

      const row = db.prepare('SELECT text FROM embeddings WHERE id = ?').get('dup-id') as any;
      expect(row.text).toBe('text 2');
    });
  });

  describe('searchSimilar', () => {
    beforeEach(async () => {
      const emb1 = await engine.generateEmbedding('machine learning');
      const emb2 = await engine.generateEmbedding('deep learning');
      const emb3 = await engine.generateEmbedding('hello world');

      engine.storeEmbedding('item-1', 'machine learning', emb1, 'source1', 1);
      engine.storeEmbedding('item-2', 'deep learning neural network', emb2, 'source2', 2);
      engine.storeEmbedding('item-3', 'hello world', emb3, 'source3', 3);
    });

    it('finds similar embeddings using cosine similarity', async () => {
      const query = await engine.generateEmbedding('neural networks');
      const results = engine.searchSimilar(query, 10);

      expect(results.length).toBeGreaterThan(0);
      expect(results[0].id).toBeDefined();
      expect(typeof results[0].similarity).toBe('number');
    });

    it('returns results sorted by similarity descending', async () => {
      const query = await engine.generateEmbedding('training');
      const results = engine.searchSimilar(query, 10);

      for (let i = 1; i < results.length; i++) {
        expect(results[i - 1].similarity).toBeGreaterThanOrEqual(results[i].similarity);
      }
    });

    it('respects limit parameter', async () => {
      const query = await engine.generateEmbedding('test query');
      const results = engine.searchSimilar(query, 2);

      expect(results.length).toBeLessThanOrEqual(2);
    });

    it('includes source and sourceLine in results', async () => {
      const query = await engine.generateEmbedding('test');
      const results = engine.searchSimilar(query, 1);

      expect(results[0].source).toBeDefined();
    });
  });

  describe('cosineSimilarity', () => {
    it('returns 1 for identical vectors', () => {
      const a = new Float32Array([1, 0, 0]);
      const b = new Float32Array([1, 0, 0]);
      expect(cosineSimilarity(a, b)).toBeCloseTo(1);
    });

    it('returns -1 for opposite vectors', () => {
      const a = new Float32Array([1, 0, 0]);
      const b = new Float32Array([-1, 0, 0]);
      expect(cosineSimilarity(a, b)).toBeCloseTo(-1);
    });

    it('returns 0 for orthogonal vectors', () => {
      const a = new Float32Array([1, 0, 0]);
      const b = new Float32Array([0, 1, 0]);
      expect(cosineSimilarity(a, b)).toBeCloseTo(0);
    });

    it('returns value between -1 and 1 for random vectors', () => {
      const a = new Float32Array([0.5, 0.3, 0.7]);
      const b = new Float32Array([0.2, 0.8, 0.1]);
      const similarity = cosineSimilarity(a, b);
      expect(similarity).toBeGreaterThanOrEqual(-1);
      expect(similarity).toBeLessThanOrEqual(1);
    });

    it('handles 384 dimensional vectors', () => {
      const a = new Float32Array(384).fill(0.1);
      const b = new Float32Array(384).fill(0.1);
      const similarity = cosineSimilarity(a, b);
      expect(similarity).toBeCloseTo(1);
    });
  });
});