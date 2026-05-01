import web_webview from '@ohos.web.webview';
import { GraphDatabase, RecallEntity, GraphMemoryService, ConnectionItem, NodeDetailInfo, Logger } from '@ohos/common';

/**
 * GraphNodeSearchBar — 图节点搜索栏
 * 悬浮在 WebView 上方的搜索输入框
 */
@Component
export struct GraphNodeSearchBar {
  @Link searchText: string;
  onSearchInput?: (value: string) => void;

  build() {
    Column() {
      TextInput({ placeholder: '搜索节点...', text: this.searchText })
        .width('80%')
        .height(40)
        .backgroundColor('rgba(10, 10, 26, 0.8)')
        .fontColor('#ffffff')
        .placeholderColor('#666688')
        .borderRadius(8)
        .border({ width: 1, color: 'rgba(100, 100, 255, 0.3)' })
        .margin({ top: 20 })
        .onChange((value: string) => {
          this.onSearchInput?.(value);
        })
    }
    .width('100%')
    .position({ x: 0, y: 0 })
    .zIndex(10)
  }
}

/**
 * NodeDetailPanel — 节点详情浮层
 * 显示选中节点的名称、类型、提及次数、连接关系
 */
@Component
export struct NodeDetailPanel {
  @Prop detail: NodeDetailInfo;
  onClose?: () => void;

  build() {
    Column() {
      Column() {
        Text(this.detail.name)
          .fontSize(18)
          .fontColor('#44ff88')
          .fontWeight(FontWeight.Bold)
          .margin({ bottom: 10 })

        Text('类型: ' + this.detail.type)
          .fontSize(14)
          .fontColor('#aaaacc')

        Text('提及次数: ' + this.detail.mention_count)
          .fontSize(14)
          .fontColor('#aaaacc')

        Text('连接数: ' + this.detail.connection_count)
          .fontSize(14)
          .fontColor('#aaaacc')

        if (this.detail.connections && this.detail.connections.length > 0) {
          Text('连接关系:')
            .fontSize(14)
            .fontColor('#8888aa')
            .margin({ top: 10, bottom: 5 })
          List() {
            ForEach(this.detail.connections, (conn: ConnectionItem) => {
              ListItem() {
                Text(conn.type + ': ' + conn.target_name)
                  .fontSize(12)
                  .fontColor('#aaaacc')
              }
            })
          }
          .height(100)
        }

        Button('关闭')
          .width(80)
          .height(30)
          .margin({ top: 15 })
          .backgroundColor('rgba(100, 100, 255, 0.3)')
          .fontColor('#ffffff')
          .onClick(() => {
            this.onClose?.();
          })
      }
      .padding(20)
      .backgroundColor('rgba(10, 10, 26, 0.95)')
      .borderRadius(12)
      .border({ width: 1, color: 'rgba(100, 100, 255, 0.3)' })
      .width(300)
    }
    .width('100%')
    .height('100%')
    .backgroundColor('rgba(0, 0, 0, 0.5)')
    .justifyContent(FlexAlign.Center)
    .alignItems(HorizontalAlign.Center)
    .zIndex(20)
  }
}

/**
 * GraphWebView — 图可视化 WebView 封装
 * 包含 WebView 配置、JS Bridge 注册、数据加载回调
 */
@Component
export struct GraphWebView {
  private controller: web_webview.WebviewController = new web_webview.WebviewController();
  private bridge?: NativeBridge;

  onPageEnd?: () => void;

  getController(): web_webview.WebviewController {
    return this.controller;
  }

  setBridge(bridge: NativeBridge): void {
    this.bridge = bridge;
  }

  build() {
    Web({ src: $rawfile('graph.html'), controller: this.controller })
      .javaScriptAccess(true)
      .width('100%')
      .height('100%')
      .zoomAccess(true)
      .onPageEnd(() => {
        this.onPageEnd?.();
      })
      .javaScriptProxy({
        object: this.bridge,
        name: 'nativeBridge',
        methodList: ['onNodeClick', 'onSearch'],
        asyncMethodList: ['requestGraphData'],
        controller: this.controller
      })
  }
}

/**
 * NativeBridge — WebView 原生桥接类（移动自 GraphPage）
 * 负责 ArkTS ↔ WebView JavaScript 双向通信
 */
export class NativeBridge {
  private controller: web_webview.WebviewController;
  private onRequestGraphData: () => void;
  private onNodeClickCallback: (nodeId: number, nodeName: string) => void;
  private onSearchCallback: (query: string) => void;

  constructor(
    controller: web_webview.WebviewController,
    onRequestGraphData: () => void,
    onNodeClickCallback: (nodeId: number, nodeName: string) => void,
    onSearchCallback: (query: string) => void
  ) {
    this.controller = controller;
    this.onRequestGraphData = onRequestGraphData;
    this.onNodeClickCallback = onNodeClickCallback;
    this.onSearchCallback = onSearchCallback;
  }

  onNodeClick(nodeId: number, nodeName: string): void {
    Logger.info('Node clicked: id=' + nodeId + ', name=' + nodeName);
    if (this.onNodeClickCallback) {
      this.onNodeClickCallback(nodeId, nodeName);
    }
  }

  onSearch(query: string): void {
    Logger.info('Search from WebView: ' + query);
    if (this.onSearchCallback) {
      this.onSearchCallback(query);
    }
  }

  requestGraphData(): void {
    Logger.info('requestGraphData called from WebView');
    if (this.onRequestGraphData) {
      this.onRequestGraphData();
    }
  }
}

/**
 * GraphDataService — 图数据查询服务
 * 封装从 GraphDatabase 读取节点和边的逻辑
 */
export class GraphDataService {
  private db: GraphDatabase;

  constructor(db: GraphDatabase) {
    this.db = db;
  }

  async getAllNodes(): Promise<GraphNodeItem[]> {
    const result = await this.db.search('');
    return result.map((r, idx): GraphNodeItem => {
      return {
        id: idx + 1,
        label: r.name,
        type: r.type,
        mentions: r.mentions
      };
    });
  }

  async getAllEdges(): Promise<GraphEdgeItem[]> {
    const recallResult = await this.db.recall('', [], 3);
    const nameToId: Record<string, number> = {};
    recallResult.entities.forEach((e: RecallEntity, idx: number): void => {
      nameToId[e.name as string] = idx + 1;
    });
    const edgeItems: GraphEdgeItem[] = [];
    for (let i = 0; i < recallResult.relations.length; i++) {
      const r = recallResult.relations[i];
      const sourceId = nameToId[r.source];
      const targetId = nameToId[r.target];
      if (sourceId !== undefined && targetId !== undefined) {
        edgeItems.push({
          id: i + 1,
          source: sourceId,
          target: targetId,
          label: r.type,
          relation: r.type
        });
      }
    }
    return edgeItems;
  }
}

// ========= 内部类型定义 =========

interface GraphNodeItem {
  id: number;
  label: string;
  type: string;
  mentions: number;
}

interface GraphEdgeItem {
  id: number;
  source: number;
  target: number;
  label: string;
  relation: string;
}