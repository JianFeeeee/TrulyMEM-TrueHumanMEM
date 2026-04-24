import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { GraphDatabase } from '/home/program/TrulyMEM-TrueHumanMEM/ts/dist/runtime/core/graph_memory/graph_database.js';
import { MemoryService } from '/home/program/TrulyMEM-TrueHumanMEM/ts/dist/runtime/core/graph_memory/memory_service.js';
import { TaskNodeStore } from '/home/program/TrulyMEM-TrueHumanMEM/ts/dist/runtime/core/graph_memory/task_node_store.js';
import * as fs from 'fs';
import * as path from 'path';

const TEST_DB_PATH = '/tmp/test_memory_service_p2.db';
const TEST_ARCHIVE_DIR = '/tmp/test_context_archive';

describe('MemoryService P2 Advanced Features', () => {
  let memoryService: MemoryService;
  let db: GraphDatabase;
  let taskStore: TaskNodeStore;

  beforeEach(async () => {
    // Clean up test files
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

    db = new GraphDatabase(TEST_DB_PATH, 'test-session-p2');
    taskStore = new TaskNodeStore(TEST_DB_PATH, TEST_ARCHIVE_DIR + '/task');
    memoryService = new MemoryService(db, taskStore, TEST_ARCHIVE_DIR);
  });

  afterEach(() => {
    if (typeof db.close === 'function') db.close();
    if (typeof taskStore.close === 'function') taskStore.close();
    if (fs.existsSync(TEST_DB_PATH)) {
      fs.unlinkSync(TEST_DB_PATH);
    }
    if (fs.existsSync(TEST_ARCHIVE_DIR)) {
      fs.rmSync(TEST_ARCHIVE_DIR, { recursive: true, force: true });
    }
  });

  describe('context_rewrite', () => {
    it('should compress context and extract key entities', async () => {
      const longContext = `用户说：我喜欢用Python编程。最近在学习TypeScript，因为想做一个全栈项目。
        我决定采用React作为前端框架，后端用FastAPI。数据库选择PostgreSQL。
        这个决策对我来说很重要，因为我希望能快速迭代。我对性能有较高要求。
        目标是三个月内上线第一个版本。`;

      const result = await memoryService.contextRewrite({
        context: longContext,
        maxEntities: 10
      });

      expect(result.extractedEntities).toBeGreaterThan(0);
      expect(result.summary.length).toBeGreaterThan(0);
      expect(result.compressed).toBe(true);
    });

    it('should detect preferences and decisions', async () => {
      const context = `用户决定使用React而不是Vue。用户喜欢简洁的代码风格。
        用户习惯每天早上检查代码质量。用户选择PostgreSQL作为数据库。`;

      const result = await memoryService.contextRewrite({
        context,
        summary: '用户技术偏好总结'
      });

      expect(result.extractedRelations).toBeGreaterThan(0);
      expect(result.summary).toBe('用户技术偏好总结');
    });
  });

  describe('working_memory_chain', () => {
    it('should retrieve working memory from task nodes', async () => {
      // First create some task nodes
      await memoryService.createTaskNode({
        session_id: 'test-session-p2',
        turn_id: 1,
        summary: '用户询问天气',
        key_facts: ['意图: 查询天气', '地点: 北京']
      });

      await memoryService.createTaskNode({
        session_id: 'test-session-p2',
        turn_id: 2,
        summary: '用户询问交通',
        key_facts: ['意图: 查询交通', '地点: 北京']
      });

      const result = await memoryService.workingMemoryChain({
        maxDepth: 2,
        recentOnly: true
      });

      expect(result.chain.length).toBeGreaterThan(0);
      expect(result.entityCount).toBeGreaterThan(0);
    });
  });

  describe('task_node chain', () => {
    it('should create task nodes and link them in chain', async () => {
      const node1 = await memoryService.createTaskNode({
        session_id: 'chain-test',
        turn_id: 1,
        summary: '开始对话',
        key_facts: ['fact1', 'fact2'],
        raw_context: '用户: 你好\nAI: 你好！有什么可以帮你的？'
      });

      expect(node1.node_id).toBeDefined();
      expect(node1.chain_linked).toBe(false); // First node

      const node2 = await memoryService.createTaskNode({
        session_id: 'chain-test',
        turn_id: 2,
        summary: '用户询问编程',
        key_facts: ['fact3'],
        raw_context: '用户: 我想学编程\nAI: 太好了！你想学什么语言？'
      });

      expect(node2.node_id).toBeDefined();
      expect(node2.chain_linked).toBe(true); // Linked to first node
    });

    it('should get recent task nodes', async () => {
      await memoryService.createTaskNode({
        session_id: 'recent-test',
        turn_id: 1,
        summary: 'Node 1',
        key_facts: ['fact1']
      });

      await memoryService.createTaskNode({
        session_id: 'recent-test',
        turn_id: 2,
        summary: 'Node 2',
        key_facts: ['fact2']
      });

      await memoryService.createTaskNode({
        session_id: 'recent-test',
        turn_id: 3,
        summary: 'Node 3',
        key_facts: ['fact3']
      });

      const recent = await memoryService.getRecentTaskNodes('recent-test', 2);
      expect(recent.length).toBe(2);
      expect(recent[0].turn_id).toBe(2); // Chronological order
      expect(recent[1].turn_id).toBe(3);
    });

    it('should get full task chain', async () => {
      await memoryService.createTaskNode({
        session_id: 'chain-full-test',
        turn_id: 1,
        summary: 'Start',
        key_facts: ['start']
      });

      await memoryService.createTaskNode({
        session_id: 'chain-full-test',
        turn_id: 2,
        summary: 'Middle',
        key_facts: ['middle']
      });

      await memoryService.createTaskNode({
        session_id: 'chain-full-test',
        turn_id: 3,
        summary: 'End',
        key_facts: ['end']
      });

      const chain = await memoryService.getTaskChain('chain-full-test');
      expect(chain.nodes.length).toBe(3);
      expect(chain.relations.length).toBe(2); // 3 nodes = 2 next relations
      expect(chain.relations[0].type).toBe('next');
    });

    it('should archive and read raw context', async () => {
      const rawContext = '这是一个很长的对话记录...包含很多细节...';

      await memoryService.createTaskNode({
        session_id: 'archive-test',
        turn_id: 1,
        summary: '对话摘要',
        key_facts: ['fact1'],
        raw_context: rawContext
      });

      const readBack = await memoryService.readArchivedContext('archive-test', 1);
      expect(readBack).toBe(rawContext);
    });
  });
});
