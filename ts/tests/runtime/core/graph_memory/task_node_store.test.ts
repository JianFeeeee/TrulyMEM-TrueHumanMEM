import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { TaskNodeStore } from '/home/program/TrulyMEM-TrueHumanMEM/ts/dist/runtime/core/graph_memory/task_node_store.js';
import * as fs from 'fs';

const TEST_DB_PATH = '/tmp/test_task_node_store.db';
const TEST_ARCHIVE_DIR = '/tmp/test_task_archive';

describe('TaskNodeStore', () => {
  let store: TaskNodeStore;

  beforeEach(async () => {
    if (fs.existsSync(TEST_DB_PATH)) {
      fs.unlinkSync(TEST_DB_PATH);
    }
    const walPath = TEST_DB_PATH + '-wal';
    const shmPath = TEST_DB_PATH + '-shm';
    if (fs.existsSync(walPath)) fs.unlinkSync(walPath);
    if (fs.existsSync(shmPath)) fs.unlinkSync(shmPath);

    if (fs.existsSync(TEST_ARCHIVE_DIR)) {
      fs.rmSync(TEST_ARCHIVE_DIR, { recursive: true, force: true });
    }

    store = new TaskNodeStore(TEST_DB_PATH, TEST_ARCHIVE_DIR);
  });

  afterEach(() => {
    if (typeof store.close === 'function') store.close();
    if (fs.existsSync(TEST_DB_PATH)) {
      fs.unlinkSync(TEST_DB_PATH);
    }
    if (fs.existsSync(TEST_ARCHIVE_DIR)) {
      fs.rmSync(TEST_ARCHIVE_DIR, { recursive: true, force: true });
    }
  });

  describe('createTaskNode', () => {
    it('should create a task node', async () => {
      const result = await store.createTaskNode({
        session_id: 'session-1',
        turn_id: 1,
        summary: 'Test summary',
        key_facts: ['fact1', 'fact2']
      });

      expect(result.node_id).toBeDefined();
      expect(result.chain_linked).toBe(false);
    });

    it('should link nodes in chain', async () => {
      await store.createTaskNode({
        session_id: 'chain-session',
        turn_id: 1,
        summary: 'First',
        key_facts: ['fact1']
      });

      const result = await store.createTaskNode({
        session_id: 'chain-session',
        turn_id: 2,
        summary: 'Second',
        key_facts: ['fact2']
      });

      expect(result.chain_linked).toBe(true);
    });

    it('should archive raw context', async () => {
      const rawContext = 'This is a long context...';
      await store.createTaskNode({
        session_id: 'archive-session',
        turn_id: 1,
        summary: 'Archived',
        key_facts: ['fact1'],
        raw_context: rawContext
      });

      const readBack = await store.readArchivedContext('archive-session', 1);
      expect(readBack).toBe(rawContext);
    });
  });

  describe('getRecentTaskNodes', () => {
    it('should return recent nodes in chronological order', async () => {
      await store.createTaskNode({
        session_id: 'recent-session',
        turn_id: 1,
        summary: 'One',
        key_facts: ['fact1']
      });
      await store.createTaskNode({
        session_id: 'recent-session',
        turn_id: 2,
        summary: 'Two',
        key_facts: ['fact2']
      });
      await store.createTaskNode({
        session_id: 'recent-session',
        turn_id: 3,
        summary: 'Three',
        key_facts: ['fact3']
      });

      const recent = await store.getRecentTaskNodes('recent-session', 2);
      expect(recent.length).toBe(2);
      expect(recent[0].turn_id).toBe(2);
      expect(recent[1].turn_id).toBe(3);
    });
  });

  describe('getTaskChain', () => {
    it('should walk full chain backwards', async () => {
      const n1 = await store.createTaskNode({
        session_id: 'walk-session',
        turn_id: 1,
        summary: 'Start',
        key_facts: ['start']
      });
      const n2 = await store.createTaskNode({
        session_id: 'walk-session',
        turn_id: 2,
        summary: 'Middle',
        key_facts: ['middle']
      });
      await store.createTaskNode({
        session_id: 'walk-session',
        turn_id: 3,
        summary: 'End',
        key_facts: ['end']
      });

      const chain = await store.getTaskChain('walk-session');
      expect(chain.nodes.length).toBe(3);
      expect(chain.relations.length).toBe(2);
    });

    it('should walk chain from specific node', async () => {
      await store.createTaskNode({
        session_id: 'from-session',
        turn_id: 1,
        summary: 'A',
        key_facts: ['a']
      });
      const n2 = await store.createTaskNode({
        session_id: 'from-session',
        turn_id: 2,
        summary: 'B',
        key_facts: ['b']
      });

      const chain = await store.getTaskChain('from-session', n2.node_id);
      expect(chain.nodes.length).toBe(2);
    });
  });
});
