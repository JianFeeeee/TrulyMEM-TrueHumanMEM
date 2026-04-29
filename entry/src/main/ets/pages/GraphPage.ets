/**
 * GraphPage — 记忆星图页面
 * 使用 WebView 显示 Three.js 3D 图可视化
 * 通过 javaScriptProxy 与 WebView 双向通信
 */
import web_webview from '@ohos.web.webview';
import { GraphDatabase, RecallEntity } from '../model/GraphDatabase';

// ========= 图数据结构定义 =========

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

// ========= WebView 原生桥接 =========

class NativeBridge {
    private controller: web_webview.WebviewController;
    private onRequestGraphData: () => void;

    constructor(controller: web_webview.WebviewController, onRequestGraphData: () => void) {
        this.controller = controller;
        this.onRequestGraphData = onRequestGraphData;
    }

    onNodeClick(nodeId: number, nodeName: string): void {
        console.info('Node clicked: id=' + nodeId + ', name=' + nodeName);
    }

    requestGraphData(): void {
        console.info('requestGraphData called from WebView');
        if (this.onRequestGraphData) {
            this.onRequestGraphData();
        }
    }
}

// ========= GraphPage 组件 =========

@Component
export struct GraphPage {
    private controller: web_webview.WebviewController = new web_webview.WebviewController();
    @Prop db: GraphDatabase;
    @State nodeCount: number = 0;
    @State edgeCount: number = 0;

    // 初始化桥接对象
    private bridge: NativeBridge = new NativeBridge(this.controller, (): void => {
        this.pushGraphDataToWebView();
    });

    /**
     * 外部触发刷新图数据（聊天写入新记忆后调用）
     */
    public async refreshGraphData(): Promise<void> {
        await this.pushGraphDataToWebView();
    }

    /**
     * 从数据库读取全量图数据，通过 runJavaScript 推送给 WebView
     */
    private async pushGraphDataToWebView(): Promise<void> {
        try {
            // 获取所有节点
            const allNodes: GraphNodeItem[] = await this.getAllNodesData();
            // 获取所有活跃关系
            const allEdges: GraphEdgeItem[] = await this.getAllEdgesData();

            // 通过 JavaScript Bridge 推送数据
            if (this.controller) {
                const jsCode: string =
                    `window.loadGraphData(${JSON.stringify({ nodes: allNodes, edges: allEdges })});`;
                this.controller.runJavaScript(jsCode);
            }

            this.nodeCount = allNodes.length;
            this.edgeCount = allEdges.length;
        } catch (err) {
            console.error('pushGraphDataToWebView error: ' + JSON.stringify(err));
        }
    }

    /**
     * 从数据库查询所有节点
     */
    private async getAllNodesData(): Promise<GraphNodeItem[]> {
        const result = await this.db.search('');
        const items: GraphNodeItem[] = result.map((r, idx): GraphNodeItem => {
            const item: GraphNodeItem = {
                id: idx + 1,
                label: r.name,
                type: r.type,
                mentions: r.mentions
            };
            return item;
        });
        return items;
    }

    /**
     * 从数据库查询所有活跃关系
     */
    private async getAllEdgesData(): Promise<GraphEdgeItem[]> {
        const recallResult = await this.db.recall('', [], 3);
        const nameToId: Record<string, number> = {};
        recallResult.entities.forEach((e: RecallEntity, idx: number): void => {
            nameToId[e.name as string] = idx + 1;
        });
        const edgeItems: GraphEdgeItem[] = [];
        for (let i = 0; i < recallResult.relations.length; i++) {
            const r = recallResult.relations[i];
            const sourceId: number | undefined = nameToId[r.source];
            const targetId: number | undefined = nameToId[r.target];
            if (sourceId !== undefined && targetId !== undefined) {
                const edgeItem: GraphEdgeItem = {
                    id: i + 1,
                    source: sourceId,
                    target: targetId,
                    label: r.type,
                    relation: r.type
                };
                edgeItems.push(edgeItem);
            }
        }
        return edgeItems;
    }

    build() {
        Column() {
            // WebView 显示 3D 星图
            Web({ src: $rawfile('graph.html'), controller: this.controller })
                .javaScriptAccess(true)
                .width('100%')
                .height('100%')
                // 页面加载完成后推送数据
                .onPageEnd(() => {
                    this.pushGraphDataToWebView();
                })
                // 注册原生桥接对象，供 WebView JavaScript 调用
                .javaScriptProxy({
                    object: this.bridge,
                    name: 'nativeBridge',
                    methodList: ['onNodeClick'],
                    asyncMethodList: ['requestGraphData'],
                    controller: this.controller
                })
        }
        .width('100%')
        .height('100%')
    }
}
