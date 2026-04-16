import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { GraphDatabase } from '/home/program/TrulyMEM-TrueHumanMEM/ts/dist/runtime/core/graph_memory/graph_database.js';

const TEST_DB_PATH = '/tmp/test_graph_memory.db';

describe('GraphDatabase', () => {
  let db: GraphDatabase;

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
    db = new GraphDatabase(TEST_DB_PATH);
  });

  afterEach(() => {
    if (db && typeof db.close === 'function') {
      db.close();
    }
  });

  describe('commit', () => {
    it('creates entities and relations', async () => {
      const result = await db.commit({
        triplets: [
          { subject: 'Alice', relation: 'knows', object: 'Bob' }
        ]
      });

      expect(result.createdEntities).toBe(2);
      expect(result.createdRelations).toBe(1);
    });

    it('handles batch multiple triplets', async () => {
      const result = await db.commit({
        triplets: [
          { subject: '用户', relation: '喜欢', object: '编程' },
          { subject: '用户', relation: '正在学习', object: 'TypeScript' },
          { subject: 'TypeScript', relation: '是', object: '语言' }
        ]
      });

      expect(result.createdEntities).toBe(6);
      expect(result.createdRelations).toBe(3);
    });
  });

  describe('recall', () => {
    beforeEach(async () => {
      await db.commit({
        triplets: [
          { subject: '用户', relation: '喜欢', object: '编程' },
          { subject: '用户', relation: '正在学习', object: 'TypeScript' },
          { subject: 'TypeScript', relation: '是', object: '语言' },
          { subject: 'Alice', relation: 'knows', object: 'Bob' }
        ]
      });
    });

    it('keyword search finds matching entities', async () => {
      const result = await db.recall({ queryIntent: '用户' });

      expect(result.entities.length).toBeGreaterThan(0);
      expect(result.entities.some(e => e.name === '用户')).toBe(true);
    });

    it('seedEntities finds exact matches', async () => {
      const result = await db.recall({
        queryIntent: 'test',
        seedEntities: ['用户']
      });

      expect(result.entities.length).toBeGreaterThan(0);
      expect(result.entities.some(e => e.name === '用户')).toBe(true);
    });

    it('sessionFilter filters by session', async () => {
      await db.commit({
        triplets: [
          { subject: 'Test', relation: 'is', object: 'Temp' }
        ],
        sessionId: 'test-session'
      });

      const result = await db.recall({
        queryIntent: 'Test',
        sessionFilter: 'test-session'
      });

      expect(result.entities.some(e => e.name === 'Test')).toBe(true);
    });

    it('finds related entities through relations', async () => {
      const result = await db.recall({
        queryIntent: '编程'
      });

      expect(result.relations.length).toBeGreaterThan(0);
    });
  });

  describe('purge', () => {
    beforeEach(async () => {
      await db.commit({
        triplets: [
          { subject: 'ToDelete', relation: 'is', object: 'Test' }
        ]
      });
    });

    it('soft delete marks relations as deleted', async () => {
      const result = await db.purge({
        criteria: { subject: 'ToDelete' },
        mode: 'soft'
      });

      expect(result.deleted).toBe(1);
      expect(result.mode).toBe('soft');
    });

    it('hard delete removes relations permanently', async () => {
      const result = await db.purge({
        criteria: { subject: 'ToDelete' },
        mode: 'hard'
      });

      expect(result.deleted).toBe(1);
      expect(result.mode).toBe('hard');
    });

    it('purge filters by target criteria', async () => {
      const result = await db.purge({
        criteria: { target: 'Test' },
        mode: 'soft'
      });

      expect(result.deleted).toBe(1);
    });

    it('purge filters by relation criteria', async () => {
      const result = await db.purge({
        criteria: { relation: 'is' },
        mode: 'soft'
      });

      expect(result.deleted).toBe(1);
    });
  });

  describe('introspect', () => {
    it('returns entity and relation counts', async () => {
      await db.commit({
        triplets: [
          { subject: 'Entity1', relation: 'relates', object: 'Entity2' }
        ]
      });

      const stats = await db.introspect();

      expect(stats.entityCount).toBe(2);
      expect(stats.relationCount).toBe(1);
      expect(stats.sessionId).toBeDefined();
    });
  });

  describe('empty query handling', () => {
    it('returns empty result for query with no matches', async () => {
      const result = await db.recall({ queryIntent: 'xyznonexistent123' });

      expect(result.entities).toEqual([]);
      expect(result.relations).toEqual([]);
    });
  });

  describe('duplicate entity handling', () => {
    it('upserts existing entities (increments mention count)', async () => {
      await db.commit({
        triplets: [
          { subject: 'Duplicate', relation: 'is', object: 'First' }
        ]
      });

      const stats1 = await db.introspect();
      const entityBefore = stats1.entityCount;

      await db.commit({
        triplets: [
          { subject: 'Duplicate', relation: 'is', object: 'Second' }
        ]
      });

      const stats2 = await db.introspect();
      const entityAfter = stats2.entityCount;

      expect(entityAfter).toBeLessThan(entityBefore + 2);
    });
  });

  describe('setSessionId and getSessionId', () => {
    it('setSessionId updates session id', async () => {
      db.setSessionId('new-session-id');

      expect(db.getSessionId()).toBe('new-session-id');
    });

    it('getSessionId returns current session id', async () => {
      const sessionId = db.getSessionId();

      expect(sessionId).toBeDefined();
      expect(typeof sessionId).toBe('string');
    });
  });
});