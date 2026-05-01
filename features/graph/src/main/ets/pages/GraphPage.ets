/**
 * GraphPage — 记忆星图页面（重构后）
 * 使用 WebView 显示 Three.js 3D 图可视化
 * 子组件：GraphWebView、GraphNodeSearchBar、NodeDetailPanel、GraphDataService、NativeBridge
 */
import web_webview from '@ohos.web.webview';
import {
  GraphDatabase,
  NodeDetailInfo,
  Logger,
  RecallEntity,
  GraphMemoryService
} from '@ohos/common';
import {
  GraphWebView,
  GraphNodeSearchBar,
  NodeDetailPanel,
  GraphDataService,
  NativeBridge
} from '../components/GraphComponents';

// ========= GraphPage 组件 =========

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

@Component
export struct GraphPage {
    private controller: web_webview.WebviewController = new web_webview.WebviewController();
    @Prop db: GraphDatabase;
    @State nodeCount: number = 0;
    @State edgeCount: number = 0;
    @State selectedNodeDetail: NodeDetailInfo | null = null;
    @State showNodeDetail: boolean = false;
    @State searchText: string = '';
    private graphService: GraphMemoryService = new GraphMemoryService(this.db);

    // 初始化桥接对象
    private bridge: NativeBridge = new NativeBridge(
        this.controller,
        (): void => { this.pushGraphDataToWebView(); },
        (nodeId: number, nodeName: string): void => { this.handleNodeClick(nodeId, nodeName); },
        (query: string): void => { this.handleSearchFromWeb(query); }
    );

    /**
     * 外部触发刷新图数据（聊天写入新记忆后调用）
     */
    public async refreshGraphData(): Promise<void> {
        await this.pushGraphDataToWebView();
    }

    /**
     * 处理节点点击 - 查询详细信息并显示浮层
     */
    private async handleNodeClick(nodeId: number, nodeName: string): Promise<void> {
        try {
            const detail: NodeDetailInfo | null = await this.graphService.getNodeDetail(nodeName);
            if (detail) {
                this.selectedNodeDetail = detail;
                this.showNodeDetail = true;
            }
        } catch (err) {
            Logger.error('handleNodeClick error: ' + JSON.stringify(err));
        }
    }

    /**
     * 处理来自 WebView 的搜索请求
     */
    private handleSearchFromWeb(query: string): void {
        this.searchText = query;
    }

    /**
     * 处理搜索输入 - 通知 WebView 过滤
     */
    private onSearchInput(value: string): void {
        this.searchText = value;
        const jsCode = `window.dispatchEvent(new MessageEvent('message', { data: { type: 'search_nodes', query: '${value}' } }));`;
        this.controller.runJavaScript(jsCode);
    }

    /**
     * 关闭节点详情浮层
     */
    private closeNodeDetail(): void {
        this.showNodeDetail = false;
        this.selectedNodeDetail = null;
    }

    /**
     * 从数据库读取全量图数据，推送给 WebView
     */
    private async getAllNodesData(): Promise<GraphNodeItem[]> {
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

    /**
     * 从数据库读取全量图数据，推送给 WebView
     */
    private async pushGraphDataToWebView(): Promise<void> {
        try {
            const allNodes: GraphNodeItem[] = await this.getAllNodesData();
            const allEdges: GraphEdgeItem[] = await this.getAllEdgesData();

            if (this.controller) {
                const jsCode: string =
                    `window.loadGraphData(${JSON.stringify({ nodes: allNodes, edges: allEdges })});`;
                this.controller.runJavaScript(jsCode);
            }

            this.nodeCount = allNodes.length;
            this.edgeCount = allEdges.length;
        } catch (err) {
            Logger.error('pushGraphDataToWebView error: ' + JSON.stringify(err));
        }
    }

    build() {
        Stack() {
            // WebView 显示 3D 星图
            Web({ src: $rawfile('graph.html'), controller: this.controller })
                .javaScriptAccess(true)
                .width('100%')
                .height('100%')
                .zoomAccess(true)
                .onPageEnd(() => {
                    this.pushGraphDataToWebView();
                })
                .javaScriptProxy({
                    object: this.bridge,
                    name: 'nativeBridge',
                    methodList: ['onNodeClick', 'onSearch'],
                    asyncMethodList: ['requestGraphData'],
                    controller: this.controller
                })

            // 搜索框
            GraphNodeSearchBar({
                searchText: this.searchText,
                onSearchInput: (value: string): void => { this.onSearchInput(value); }
            })

            // 节点详情浮层
            if (this.showNodeDetail && this.selectedNodeDetail !== null) {
                NodeDetailPanel({
                    detail: this.selectedNodeDetail,
                    onClose: (): void => { this.closeNodeDetail(); }
                })
            }
        }
        .width('100%')
        .height('100%')
    }
}