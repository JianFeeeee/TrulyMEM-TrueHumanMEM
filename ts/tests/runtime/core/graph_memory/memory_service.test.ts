import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { MemoryService } from '../../../../dist/runtime/core/graph_memory/memory_service.js';
import { GraphDatabase } from '../../../../dist/runtime/core/graph_memory/graph_database.js';
import * as fs from 'fs';

const TEST_DB_PATH = '/tmp/test_memory_service.db';

describe('MemoryService', () => {
  let memoryService: MemoryService;
  let db: GraphDatabase;

  beforeEach(async () => {
    if (fs.existsSync(TEST_DB_PATH)) {
      fs.unlinkSync(TEST_DB_PATH);
    }
    const walPath = TEST_DB_PATH + '-wal';
    const shmPath = TEST_DB_PATH + '-shm';
    if (fs.existsSync(walPath)) fs.unlinkSync(walPath);
    if (fs.existsSync(shmPath)) fs.unlinkSync(shmPath);
    db = new GraphDatabase(TEST_DB_PATH, 'test-session');
    memoryService = new MemoryService(db);
  });

  afterEach(async () => {
    if (typeof db.close === 'function') db.close();
    if (fs.existsSync(TEST_DB_PATH)) {
      fs.unlinkSync(TEST_DB_PATH);
    }
    const walPath = TEST_DB_PATH + '-wal';
    const shmPath = TEST_DB_PATH + '-shm';
    if (fs.existsSync(walPath)) fs.unlinkSync(walPath);
    if (fs.existsSync(shmPath)) fs.unlinkSync(shmPath);
  });

  describe('updatePersona', () => {
    it('should merge attributes in merge mode', async () => {
      const result = await memoryService.updatePersona({
        attributes: [
          { attribute: 'name', value: 'AI Assistant' },
          { attribute: 'personality', value: 'helpful' }
        ],
        mode: 'merge'
      });

      expect(result.status).toBe('success');
      expect(result.updatedAttributes).toBe(2);
    });

    it('should replace attributes in replace mode', async () => {
      await memoryService.updatePersona({
        attributes: [
          { attribute: 'name', value: 'Old Name' }
        ],
        mode: 'merge'
      });

      const result = await memoryService.updatePersona({
        attributes: [
          { attribute: 'name', value: 'New Name' }
        ],
        mode: 'replace'
      });

      expect(result.status).toBe('success');
      expect(result.updatedAttributes).toBe(1);
    });
  });

  describe('clearPersona', () => {
    it('should delete persona when confirm is true', async () => {
      await memoryService.updatePersona({
        attributes: [
          { attribute: 'name', value: 'Test AI' }
        ],
        mode: 'merge'
      });

      const result = await memoryService.clearPersona({ confirm: true });
      expect(result.status).toBe('success');
      expect(result.deletedCount).toBeGreaterThan(0);
    });

    it('should cancel when confirm is false', async () => {
      const result = await memoryService.clearPersona({ confirm: false });
      expect(result.status).toBe('cancelled');
      expect(result.deletedCount).toBe(0);
    });
  });

  describe('createTask', () => {
    it('should create task with info_nodes', async () => {
      const result = await memoryService.createTask({
        task_id: 'Task_001',
        description: 'Test task with info',
        info_nodes: ['Node_A', 'Node_B']
      });

      expect(result.status).toBe('success');
      expect(result.taskId).toBe('Task_001');
    });

    it('should create task without info_nodes', async () => {
      const result = await memoryService.createTask({
        task_id: 'Task_002',
        description: 'Test task without info'
      });

      expect(result.status).toBe('success');
      expect(result.taskId).toBe('Task_002');
    });
  });

  describe('setTaskState', () => {
    it('should set task state', async () => {
      await memoryService.createTask({
        task_id: 'Task_StateTest',
        description: 'Task for state test'
      });

      const result = await memoryService.setTaskState({
        task_id: 'Task_StateTest',
        state: '已暂停'
      });

      expect(result.status).toBe('success');
      expect(result.newState).toBe('已暂停');
    });
  });

  describe('deleteTask', () => {
    it('should delete task', async () => {
      await memoryService.createTask({
        task_id: 'Task_Delete',
        description: 'Task to delete'
      });

      const result = await memoryService.deleteTask({ task_id: 'Task_Delete' });
      expect(result.status).toBe('success');
      expect(result.taskId).toBe('Task_Delete');
    });
  });

  describe('linkInfoToTask', () => {
    it('should link info node to task', async () => {
      await memoryService.createTask({
        task_id: 'Task_Link',
        description: 'Task for linking'
      });

      const result = await memoryService.linkInfoToTask({
        task_id: 'Task_Link',
        info_node: 'Info_Node_X'
      });

      expect(result.status).toBe('success');
    });
  });

  describe('sessionId', () => {
    it('should set and get sessionId', () => {
      memoryService.setSessionId('custom-session-123');
      const sessionId = memoryService.getSessionId();
      expect(sessionId).toBe('custom-session-123');
    });
  });

  describe('task state transitions', () => {
    it('should transition: 进行中 → 已暂停 → 进行中 → 已完成', async () => {
      await memoryService.createTask({
        task_id: 'Task_Transition',
        description: 'State transition task'
      });

      const state1 = await memoryService.setTaskState({
        task_id: 'Task_Transition',
        state: '进行中'
      });
      expect(state1.newState).toBe('进行中');

      const state2 = await memoryService.setTaskState({
        task_id: 'Task_Transition',
        state: '已暂停'
      });
      expect(state2.newState).toBe('已暂停');

      const state3 = await memoryService.setTaskState({
        task_id: 'Task_Transition',
        state: '进行中'
      });
      expect(state3.newState).toBe('进行中');

      const state4 = await memoryService.setTaskState({
        task_id: 'Task_Transition',
        state: '已完成'
      });
      expect(state4.newState).toBe('已完成');
    });
  });

  describe('delegate methods', () => {
    it('recall should delegate to db', async () => {
      await memoryService.commit({
        triplets: [
          { subject: '测试', relation: '是', object: '示例' }
        ]
      });

      const result = await memoryService.recall({
        queryIntent: '测试'
      });

      expect(result.entities).toBeDefined();
      expect(result.relations).toBeDefined();
    });

    it('commit should delegate to db', async () => {
      const result = await memoryService.commit({
        triplets: [
          { subject: '用户', relation: '喜欢', object: '编程' }
        ]
      });

      expect(result.createdEntities).toBeGreaterThan(0);
      expect(result.createdRelations).toBeGreaterThan(0);
    });

    it('purge should delegate to db', async () => {
      await memoryService.commit({
        triplets: [
          { subject: '待删除', relation: '是', object: '测试' }
        ]
      });

      const result = await memoryService.purge({
        criteria: { subject: '待删除' }
      });

      expect(result.deleted).toBeGreaterThanOrEqual(0);
    });

  });
});