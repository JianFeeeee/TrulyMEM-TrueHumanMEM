import { GraphDatabase } from './graph_database.js';
import { TaskNodeStore } from './task_node_store.js';
import * as fs from 'fs';
import * as path from 'path';
import type {
  RecallParams, CommitParams, PurgeParams,
  RecallResult, CommitResult, PurgeResult, MemoryStats,
  ContextRewriteParams, ContextRewriteResult,
  WorkingMemoryChainParams, WorkingMemoryChainResult,
  TaskNodeCreateParams, TaskNodeChainResult
} from './types.js';

export class MemoryService {
  private db: GraphDatabase;
  private taskStore: TaskNodeStore;
  private contextArchiveDir: string;

  constructor(db: GraphDatabase, taskStore?: TaskNodeStore, archiveDir?: string) {
    this.db = db;
    this.taskStore = taskStore || new TaskNodeStore();
    this.contextArchiveDir = archiveDir || './context_archive';
    if (!fs.existsSync(this.contextArchiveDir)) {
      fs.mkdirSync(this.contextArchiveDir, { recursive: true });
    }
  }

  async recall(params: RecallParams): Promise<RecallResult> {
    return this.db.recall(params);
  }

  async commit(params: CommitParams): Promise<CommitResult> {
    return this.db.commit(params);
  }

  async purge(params: PurgeParams): Promise<PurgeResult> {
    return this.db.purge(params);
  }

  async introspect(): Promise<MemoryStats> {
    return this.db.introspect();
  }

  async archive(days: number = 30): Promise<{ archived: number }> {
    return this.db.archive(days);
  }

  async cleanup(dryRun: boolean = true): Promise<{ deleted_relations: number; deleted_entities: number; details?: string[] }> {
    return this.db.cleanup(dryRun);
  }

  // ========== Persona ==========

  async updatePersona(params: { attributes: Array<{ attribute: string; value: string }>; mode?: 'merge' | 'replace' }): Promise<{ status: string; updatedAttributes: number }> {
    const { attributes, mode = 'merge' } = params;

    if (mode === 'replace') {
      await this.db.purge({
        criteria: { subject: 'AI' },
        mode: 'soft'
      });
    }

    const triplets = attributes.map(attr => ({
      subject: 'AI',
      relation: attr.attribute,
      object: attr.value,
      confidence: 1.0
    }));

    await this.db.commit({ triplets });

    return { status: 'success', updatedAttributes: attributes.length };
  }

  async clearPersona(params: { confirm: boolean }): Promise<{ status: string; deletedCount: number }> {
    if (params.confirm === false) {
      return { status: 'cancelled', deletedCount: 0 };
    }

    const result = await this.db.purge({
      criteria: { subject: 'AI' },
      mode: 'soft'
    });

    return { status: 'success', deletedCount: result.deleted };
  }

  async createTask(params: { task_id: string; description: string; info_nodes?: string[] | undefined }): Promise<{ status: string; taskId: string }> {
    const { task_id, description, info_nodes = [] } = params;

    await this.db.commit({
      triplets: [
        { subject: task_id, relation: 'is_type', object: 'TaskNode' },
        { subject: task_id, relation: 'has_description', object: description },
        { subject: task_id, relation: 'HAS_STATE', object: 'State_进行中' }
      ]
    });

    if (info_nodes.length > 0) {
      await this.db.commit({
        triplets: info_nodes.map(node => ({
          subject: task_id,
          relation: 'CONTAINS_INFO',
          object: node
        }))
      });
    }

    return { status: 'success', taskId: task_id };
  }

  async setTaskState(params: { task_id: string; state: string }): Promise<{ status: string; newState: string }> {
    const { task_id, state } = params;

    await this.db.purge({
      criteria: { subject: task_id, relation: 'HAS_STATE' },
      mode: 'soft'
    });

    await this.db.commit({
      triplets: [{ subject: task_id, relation: 'HAS_STATE', object: `State_${state}` }]
    });

    return { status: 'success', newState: state };
  }

  async deleteTask(params: { task_id: string }): Promise<{ status: string; taskId: string }> {
    const { task_id } = params;

    await this.db.purge({
      criteria: { subject: task_id },
      mode: 'soft'
    });

    return { status: 'success', taskId: task_id };
  }

  async linkInfoToTask(params: { task_id: string; info_node: string }): Promise<{ status: string }> {
    const { task_id, info_node } = params;

    await this.db.commit({
      triplets: [{ subject: task_id, relation: 'CONTAINS_INFO', object: info_node }]
    });

    return { status: 'success' };
  }

  // ========== TaskNode Chain ==========

  async createTaskNode(params: TaskNodeCreateParams): Promise<{ node_id: number; chain_linked: boolean; archived_path: string | undefined }> {
    const result = await this.taskStore.createTaskNode(params);

    // Also archive raw context if provided
    let archivedPath: string | undefined = undefined;
    if (params.raw_context) {
      archivedPath = path.join(this.contextArchiveDir, `${params.session_id}_turn${params.turn_id}_raw.txt`);
      fs.writeFileSync(archivedPath, params.raw_context, 'utf-8');
    }

    return { ...result, archived_path: archivedPath };
  }

  async getRecentTaskNodes(session_id: string, limit: number = 5): Promise<Array<{ id: number; turn_id: number; summary: string; key_facts: string[]; created_at: string }>> {
    const nodes = await this.taskStore.getRecentTaskNodes(session_id, limit);
    return nodes.map(n => ({
      id: n.id,
      turn_id: n.turn_id,
      summary: n.summary,
      key_facts: JSON.parse(n.key_facts || '[]') as string[],
      created_at: n.created_at
    }));
  }

  async getTaskChain(session_id: string, from_node_id?: number): Promise<TaskNodeChainResult> {
    return this.taskStore.getTaskChain(session_id, from_node_id);
  }

  async readArchivedContext(session_id: string, turn_id: number): Promise<string | null> {
    const archivePath = path.join(this.contextArchiveDir, `${session_id}_turn${turn_id}_raw.txt`);
    if (fs.existsSync(archivePath)) {
      return fs.readFileSync(archivePath, 'utf-8');
    }
    return null;
  }

  // ========== Context Rewrite ==========

  async contextRewrite(params: ContextRewriteParams): Promise<ContextRewriteResult> {
    const { context, maxEntities = 20, summary } = params;

    // 1. 提取关键句子
    const sentences = context
      .split(/[。！？\n]+/)
      .map(s => s.trim())
      .filter(s => s.length > 5 && s.length < 200);

    // 2. 提取实体（使用增强规则）
    const entityPattern = /(?:我|你|用户|AI|系统|项目|任务|文件|代码|程序|功能|接口|类|方法|变量|数据库|服务器|客户端|前端|后端|API|Web|App|Python|JavaScript|TypeScript|Java|Go|Rust|C\+\+|数据库|图|记忆|插件|工具|技能|记忆|上下文|偏好|习惯|决策|重要|关键|目标|计划|问题|解决|方案|结果|选择|决定|配置|环境|版本|分支|提交|合并|发布|部署|测试|调试|优化|重构|设计|架构|模式|框架|库|包|依赖|构建|编译|运行|执行|输出|输入|错误|异常|警告|日志|监控|性能|安全|权限|认证|授权|缓存|队列|消息|事件|状态|数据|模型|视图|控制器|路由|请求|响应|协议|格式|编码|解析|序列化|反序列化|同步|异步|并行|并发|线程|进程|阻塞|非阻塞|流|管道|过滤|映射|归约|排序|搜索|匹配|替换|分割|合并|压缩|解压|加密|解密|签名|验证|哈希|随机|唯一|索引|主键|外键|约束|事务|回滚|提交|锁|死锁|超时|重试|降级|熔断|限流|负载|均衡|路由|网关|代理|转发|重写|镜像|快照|备份|恢复|复制|分片|分区|集群|节点|拓扑|网络|域名|IP|端口|套接字|连接|会话|Cookie|Token|JWT|OAuth|SSO|LDAP|AD|Kerberos|证书|CA|TLS|SSL|HTTPS|HTTP|TCP|UDP|WebSocket|gRPC|REST|GraphQL|SOAP|XML|JSON|YAML|TOML|INI|CSV|TSV|Markdown|HTML|CSS|Sass|Less|Stylus|PostCSS|Tailwind|Bootstrap|jQuery|React|Vue|Angular|Svelte|Next|Nuxt|Express|Koa|Fastify|Nest|Django|Flask|FastAPI|Tornado|Spring|Laravel|Rails|Sinatra|Phoenix|Lumen|CodeIgniter|Symfony|Zend|Cake|Fuel|Yii|Phalcon|Slim|Mezzio|Laminas|Expressive|Struts|JSF|GWT|Vaadin|Wicket|Play|Akka|Vert|Quarkus|Micronaut|Helidon|Ktor|http4k|Javalin|Spark|Dropwizard|SpringBoot|Micronaut|Quarkus|Helidon|Ktor|http4k|Javalin|Spark|Dropwizard|Guice|Dagger|Spring|CDI|OSGi|EJB|JPA|Hibernate|MyBatis|EclipseLink|OpenJPA|DataNucleus|ObjectDB|Versant|db4o|NeoDatis|Perst|H2|SQLite|MySQL|PostgreSQL|Oracle|SQLServer|DB2|Sybase|Informix|Teradata|Vertica|Greenplum|Redshift|BigQuery|Snowflake|Databricks|SparkSQL|Hive|Impala|Presto|Trino|Drill|Phoenix|HBase|Cassandra|MongoDB|CouchDB|DynamoDB|DocumentDB|Firestore|CosmosDB|Redis|Memcached|Riak|Voldemort|Couchbase|Aerospike|Scylla| Yugabyte|TiDB|Cockroach|Vitess|ProxySQL|MaxScale|PgBouncer|Odyssey| Pgpool|Slony|Bucardo|Londiste|Skytools|WalE|Barman|PgBackRest|PgDump| PgRestore|PgUpgrade|PgAdmin|PgStudio|OmniDB|DBeaver|Navicat|DataGrip| TablePlus|SequelPro|HeidiSQL|MySQLWorkbench|phpMyAdmin|Adminer|SQLBuddy| Chive|TinyTinyRSS|FreshRSS|Miniflux|Stringer|Feedly|Inoreader|NewsBlur| TheOldReader|CommaFeed|BazQux|Feedbin|Feed Wrangler|FeedHQ|FeedReader| Liferea|QuiteRSS|RSSOwl|Thunderbird|Outlook|AppleMail|Spark|Airmail| Newton|Canary|Edison|BlueMail|TypeApp|Nine|K9|FairEmail|Aquamail| ProtonMail|Tutanota|CTemplar|StartMail|Runbox|CounterMail|Hushmail| KolabNow|Mailbox.org|Posteo|Soverin|TheXYZ|ZohoMail|FastMail|GandiMail| Namecheap|Hover|DreamHost|HostGator|Bluehost|GoDaddy|Namecheap|Dynadot| GoogleDomains|CloudflareRegistrar|Route53|DNSimple|Gandi|OVH|Hetzner| Linode|DigitalOcean|Vultr|UpCloud|Scaleway|Exoscale|CherryServers| Packet|Equinix|AWS|Azure|GCP|IBMCloud|OracleCloud|AlibabaCloud|TencentCloud| HuaweiCloud|BaiduCloud|JDCloud|UCloud|QingCloud|ChinaTelecom|ChinaUnicom| ChinaMobile|GreatWall|DrPeng|Broadnet|Wasu|Born|Topway|Guangdong| Guangxi|Hainan|Chongqing|Sichuan|Guizhou|Yunnan|Xizang|Shaanxi| Gansu|Qinghai|Ningxia|Xinjiang|Beijing|Tianjin|Hebei|Shanxi|InnerMongolia| Liaoning|Jilin|Heilongjiang|Shanghai|Jiangsu|Zhejiang|Anhui|Fujian| Jiangxi|Shandong|Henan|Hubei|Hunan|Guangdong|Guangxi|Hainan|Chongqing| Sichuan|Guizhou|Yunnan|Xizang|Shaanxi|Gansu|Qinghai|Ningxia|Xinjiang| HongKong|Macau|Taiwan)/g;
    const foundEntities = new Set<string>();
    sentences.forEach(s => {
      const matches = s.match(entityPattern);
      if (matches) matches.forEach(m => foundEntities.add(m));
    });

    if (foundEntities.size < 3) {
      const words = context.split(/\s+/).filter(w => w.length >= 2 && w.length <= 20);
      const freq = new Map<string, number>();
      words.forEach(w => freq.set(w, (freq.get(w) || 0) + 1));
      const sorted = [...freq.entries()].sort((a, b) => b[1] - a[1]);
      sorted.slice(0, maxEntities).forEach(([w]) => foundEntities.add(w));
    }

    const entities = Array.from(foundEntities).slice(0, maxEntities);

    // 3. 生成摘要
    const keySentences = sentences
      .filter(s => entities.some(e => s.includes(e)))
      .slice(0, 5);

    const generatedSummary = summary || keySentences.join('；') || context.slice(0, 200);

    // 4. 生成三元组关系
    const triplets: Array<{ subject: string; relation: string; object: string; confidence?: number }> = [];

    // 实体共现关系
    for (let i = 0; i < Math.min(entities.length, 10); i++) {
      for (let j = i + 1; j < Math.min(entities.length, 10); j++) {
        const s1 = entities[i];
        const s2 = entities[j];
        const coOccur = sentences.some(s => s.includes(s1) && s.includes(s2));
        if (coOccur) {
          triplets.push({
            subject: s1,
            relation: '关联',
            object: s2,
            confidence: 0.7
          });
        }
      }
    }

    // 检测偏好和决策模式
    const preferencePatterns = [
      { pattern: /喜欢|偏好|爱好|倾向|习惯|常用|总是|经常/, relation: '偏好' },
      { pattern: /决定|决策|选择|确定|定了|采用|使用|方案/, relation: '决策' },
      { pattern: /重要|关键|核心|主要|首要|必须|务必|一定/, relation: '重要性' },
      { pattern: /目标|计划|打算|准备|预计|期望|希望|想要/, relation: '意图' },
      { pattern: /问题|错误|异常|失败|困难|挑战|障碍|风险/, relation: '问题' },
      { pattern: /解决|修复|处理|应对|克服|消除|避免|预防/, relation: '解决方案' }
    ];

    sentences.forEach(sentence => {
      preferencePatterns.forEach(({ pattern, relation }) => {
        if (pattern.test(sentence)) {
          const matchedEntities = entities.filter(e => sentence.includes(e));
          if (matchedEntities.length > 0) {
            triplets.push({
              subject: matchedEntities[0],
              relation,
              object: sentence.slice(0, 100),
              confidence: 0.85
            });
          }
        }
      });
    });

    // 创建摘要节点
    const summaryId = `Summary_${Date.now()}`;
    triplets.push({
      subject: summaryId,
      relation: 'is_type',
      object: 'ContextSummary',
      confidence: 1.0
    });
    triplets.push({
      subject: summaryId,
      relation: 'HAS_CONTENT',
      object: generatedSummary.slice(0, 500),
      confidence: 1.0
    });
    triplets.push({
      subject: summaryId,
      relation: 'SOURCE_TYPE',
      object: 'context_rewrite',
      confidence: 1.0
    });

    // 实体与摘要的关联
    entities.slice(0, 5).forEach(e => {
      triplets.push({
        subject: summaryId,
        relation: 'MENTIONS',
        object: e,
        confidence: 0.8
      });
    });

    // 写入记忆图
    const commitResult = await this.db.commit({ triplets });

    // 同时存入任务节点表
    const keyFacts = entities.slice(0, 10).map(e => `实体: ${e}`);
    keyFacts.push(`摘要: ${generatedSummary.slice(0, 100)}`);

    await this.taskStore.createTaskNode({
      session_id: this.db.getSessionId(),
      turn_id: Date.now(),
      summary: generatedSummary,
      key_facts: keyFacts,
      raw_context: context
    });

    return {
      extractedEntities: entities.length,
      extractedRelations: commitResult.createdRelations,
      summary: generatedSummary,
      compressed: context.length > generatedSummary.length
    };
  }

  // ========== Working Memory Chain ==========

  async workingMemoryChain(params: WorkingMemoryChainParams = {}): Promise<WorkingMemoryChainResult> {
    const { maxDepth = 3, recentOnly = true } = params;

    // 使用 TaskNode 链获取工作记忆
    const sessionId = this.db.getSessionId();
    const recentNodes = await this.taskStore.getRecentTaskNodes(sessionId, maxDepth * 3);

    const chain = recentNodes.map(n => ({
      subject: `Turn_${n.turn_id}`,
      relation: 'summary',
      object: n.summary.slice(0, 100),
      timestamp: n.created_at
    }));

    // 同时从图数据库获取活跃关系补充
    const timeFilter = recentOnly ? { days: 1 } : undefined;
    const graphResult = await this.db.recall({
      queryIntent: '',
      seedEntities: [],
      depth: maxDepth,
      timeRange: timeFilter,
      sessionFilter: sessionId
    });

    const graphChain = graphResult.relations
      .filter(r => r.status === 'active')
      .slice(0, 10)
      .map(r => {
        const source = graphResult.entities.find(e => e.id === r.sourceId);
        const target = graphResult.entities.find(e => e.id === r.targetId);
        return {
          subject: source?.name || r.sourceId,
          relation: r.relationType,
          object: target?.name || r.targetId,
          timestamp: r.createdAt.toISOString()
        };
      });

    return {
      chain: [...chain, ...graphChain].slice(0, 20),
      entityCount: graphResult.entities.length + recentNodes.length
    };
  }

  // ========== Utility ==========

  setSessionId(sessionId: string): void {
    this.db.setSessionId(sessionId);
  }

  getSessionId(): string {
    return this.db.getSessionId();
  }
}
