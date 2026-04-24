export interface Entity {
  id: string;
  name: string;
  type: string;
  mentionCount: number;
  createdAt: Date;
  updatedAt: Date;
}

export type RelationStatus = 'active' | 'deleted' | 'archived' | 'superseded';

export interface Relation {
  id: string;
  sourceId: string;
  targetId: string;
  relationType: string;
  confidence: number;
  status: RelationStatus;
  sessionId: string;
  turnId: number;
  createdAt: Date;
  updatedAt: Date;
  dateBucket: string;
}

export interface Triplet {
  subject: string;
  relation: string;
  object: string;
  confidence?: number;
}

export interface RecallParams {
  queryIntent: string;
  seedEntities?: string[] | undefined;
  depth?: number | undefined;
  timeRange?: { days: number } | undefined;
  sessionFilter?: string | undefined;
}

export interface CommitParams {
  triplets: Triplet[];
  entityTypes?: Record<string, string> | undefined;
  temporalTag?: string | undefined;
  sessionId?: string | undefined;
  turnId?: number | undefined;
}

export interface PurgeParams {
  criteria?: {
    subject?: string | undefined;
    target?: string | undefined;
    relation?: string | undefined;
    sessionId?: string | undefined;
  } | undefined;
  mode?: 'soft' | 'hard' | 'supersede' | undefined;
  newRelation?: { relation: string; target: string } | undefined;
}

export interface RecallResult {
  entities: Entity[];
  relations: Relation[];
  message: string;
}

export interface CommitResult {
  createdEntities: number;
  createdRelations: number;
}

export interface PurgeResult {
  deleted: number;
  mode: string;
}

export type TaskState = '进行中' | '已完成' | '已暂停' | '已取消';

export interface Task {
  taskId: string;
  description: string;
  state: TaskState;
  infoNodes: string[];
  createdAt: Date;
  updatedAt: Date;
}

export interface MemoryStats {
  entityCount: number;
  relationCount: number;
  sessionId?: string;
}

export interface PersonaAttribute {
  attribute: string;
  value: string;
}

export interface PersonaUpdateParams {
  attributes: PersonaAttribute[];
  mode?: 'merge' | 'replace';
}

export interface PersonaClearParams {
  confirm: boolean;
}

export interface TaskCreateParams {
  task_id: string;
  description: string;
  info_nodes?: string[] | undefined;
}

export interface TaskSetStateParams {
  task_id: string;
  state: string;
}

export interface TaskDeleteParams {
  task_id: string;
}

export interface TaskLinkInfoParams {
  task_id: string;
  info_node: string;
}

export interface ContextRewriteParams {
  context: string;
  maxEntities?: number | undefined;
  summary?: string | undefined;
}

export interface ContextRewriteResult {
  extractedEntities: number;
  extractedRelations: number;
  summary: string;
  compressed: boolean;
}

export interface WorkingMemoryChainParams {
  maxDepth?: number | undefined;
  recentOnly?: boolean | undefined;
}

export interface WorkingMemoryChainResult {
  chain: Array<{ subject: string; relation: string; object: string; timestamp: string }>;
  entityCount: number;
}

export interface TaskNodeData {
  id: number;
  session_id: string;
  turn_id: number;
  summary: string;
  key_facts: string;
  created_at: string;
}

export interface TaskNodeCreateParams {
  session_id: string;
  turn_id: number;
  summary: string;
  key_facts: string[];
  raw_context?: string | undefined;
}

export interface TaskNodeChainResult {
  nodes: TaskNodeData[];
  relations: Array<{ from: number; to: number; type: string }>;
}
