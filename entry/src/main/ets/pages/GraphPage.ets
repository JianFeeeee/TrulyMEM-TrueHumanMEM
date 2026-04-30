/**
 * GraphPage — 记忆星图页面
 * 使用 WebView 显示 Three.js 3D 图可视化
 * 通过 javaScriptProxy 与 WebView 双向通信
 */
import web_webview from '@ohos.web.webview';
import { GraphDatabase, RecallEntity } from '../model/GraphDatabase';
import { GraphMemoryService } from '../services/GraphMemoryService';

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

interface NodeDetailInfo {
    name: string;
    type: string;
    mention_count: number;
    connection_count: number;
    connections: Array<{ type: string; target_name: string }>;
}

// ========= WebView 原生桥接 =========

class NativeBridge {
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
        console.info('Node clicked: id=' + nodeId + ', name=' + nodeName);
        if (this.onNodeClickCallback) {
            this.onNodeClickCallback(nodeId, nodeName);
        }
    }

    onSearch(query: string): void {
        console.info('Search from WebView: ' + query);
        if (this.onSearchCallback) {
            this.onSearchCallback(query);
        }
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
            // 从数据库查询节点详细信息
            const detail = await this.graphService.getNodeDetail(nodeName);
            if (detail) {
                this.selectedNodeDetail = detail;
                this.showNodeDetail = true;
            }
        } catch (err) {
            console.error('handleNodeClick error: ' + JSON.stringify(err));
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
        Stack() {
            // WebView 显示 3D 星图
            Web({ src: $rawfile('graph.html'), controller: this.controller })
                .javaScriptAccess(true)
                .width('100%')
                .height('100%')
                .zoomAccess(true) // 启用缩放
                // 捏合手势支持 - 双指缩放
                .pinchGesture(PinchGesture({ fingers: 2 }))
                .onPageEnd(() => {
                    this.pushGraphDataToWebView();
                })
                // 注册原生桥接对象，供 WebView JavaScript 调用
                .javaScriptProxy({
                    object: this.bridge,
                    name: 'nativeBridge',
                    methodList: ['onNodeClick', 'onSearch'],
                    asyncMethodList: ['requestGraphData'],
                    controller: this.controller
                })

            // 搜索框组件 - 在 WebView 上方
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
                        this.onSearchInput(value);
                    })
            }
            .width('100%')
            .alignContent(Alignment.Top)
            .position({ x: 0, y: 0 })
            .zIndex(10)

            // 节点详情浮层
            if (this.showNodeDetail && this.selectedNodeDetail !== null) {
                Column() {
                    Column() {
                        Text(this.selectedNodeDetail.name)
                            .fontSize(18)
                            .fontColor('#44ff88')
                            .fontWeight(FontWeight.Bold)
                            .margin({ bottom: 10 })

                        Text('类型: ' + this.selectedNodeDetail.type)
                            .fontSize(14)
                            .fontColor('#aaaacc')

                        Text('提及次数: ' + this.selectedNodeDetail.mention_count)
                            .fontSize(14)
                            .fontColor('#aaaacc')

                        Text('连接数: ' + this.selectedNodeDetail.connection_count)
                            .fontSize(14)
                            .fontColor('#aaaacc')

                        if (this.selectedNodeDetail.connections && this.selectedNodeDetail.connections.length > 0) {
                            Text('连接关系:')
                                .fontSize(14)
                                .fontColor('#8888aa')
                                .margin({ top: 10, bottom: 5 })
                            List() {
                                ForEach(this.selectedNodeDetail.connections, (conn: { type: string; target_name: string }) => {
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
                                this.closeNodeDetail();
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
        .width('100%')
        .height('100%')
    }
}
