if (!("finalizeConstruction" in ViewPU.prototype)) {
    Reflect.set(ViewPU.prototype, "finalizeConstruction", () => { });
}
interface GraphPage_Params {
    controller?: web_webview.WebviewController;
    db?: GraphDatabase;
    nodeCount?: number;
    edgeCount?: number;
    selectedNodeDetail?: NodeDetailInfo | null;
    showNodeDetail?: boolean;
    searchText?: string;
    graphService?: GraphMemoryService;
    bridge?: NativeBridge;
}
import web_webview from "@ohos:web.webview";
import { Logger, GraphMemoryService } from "@normalized:N&&&@ohos/common/Index&1.0.0";
import type { GraphDatabase, NodeDetailInfo, RecallEntity } from "@normalized:N&&&@ohos/common/Index&1.0.0";
import { GraphNodeSearchBar, NodeDetailPanel, NativeBridge } from "@normalized:N&&&@ohos/graph/src/main/ets/components/GraphComponents&1.0.0";
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
export class GraphPage extends ViewPU {
    constructor(parent, params, __localStorage, elmtId = -1, paramsLambda = undefined, extraInfo) {
        super(parent, __localStorage, elmtId, extraInfo);
        if (typeof paramsLambda === "function") {
            this.paramsGenerator_ = paramsLambda;
        }
        this.controller = new web_webview.WebviewController();
        this.__db = new SynchedPropertyObjectOneWayPU(params.db, this, "db");
        this.__nodeCount = new ObservedPropertySimplePU(0, this, "nodeCount");
        this.__edgeCount = new ObservedPropertySimplePU(0, this, "edgeCount");
        this.__selectedNodeDetail = new ObservedPropertyObjectPU(null, this, "selectedNodeDetail");
        this.__showNodeDetail = new ObservedPropertySimplePU(false, this, "showNodeDetail");
        this.__searchText = new ObservedPropertySimplePU('', this, "searchText");
        this.graphService = undefined;
        this.bridge = undefined;
        this.setInitiallyProvidedValue(params);
        this.finalizeConstruction();
    }
    setInitiallyProvidedValue(params: GraphPage_Params) {
        if (params.controller !== undefined) {
            this.controller = params.controller;
        }
        if (params.nodeCount !== undefined) {
            this.nodeCount = params.nodeCount;
        }
        if (params.edgeCount !== undefined) {
            this.edgeCount = params.edgeCount;
        }
        if (params.selectedNodeDetail !== undefined) {
            this.selectedNodeDetail = params.selectedNodeDetail;
        }
        if (params.showNodeDetail !== undefined) {
            this.showNodeDetail = params.showNodeDetail;
        }
        if (params.searchText !== undefined) {
            this.searchText = params.searchText;
        }
        if (params.graphService !== undefined) {
            this.graphService = params.graphService;
        }
        if (params.bridge !== undefined) {
            this.bridge = params.bridge;
        }
    }
    updateStateVars(params: GraphPage_Params) {
        this.__db.reset(params.db);
    }
    purgeVariableDependenciesOnElmtId(rmElmtId) {
        this.__db.purgeDependencyOnElmtId(rmElmtId);
        this.__nodeCount.purgeDependencyOnElmtId(rmElmtId);
        this.__edgeCount.purgeDependencyOnElmtId(rmElmtId);
        this.__selectedNodeDetail.purgeDependencyOnElmtId(rmElmtId);
        this.__showNodeDetail.purgeDependencyOnElmtId(rmElmtId);
        this.__searchText.purgeDependencyOnElmtId(rmElmtId);
    }
    aboutToBeDeleted() {
        this.__db.aboutToBeDeleted();
        this.__nodeCount.aboutToBeDeleted();
        this.__edgeCount.aboutToBeDeleted();
        this.__selectedNodeDetail.aboutToBeDeleted();
        this.__showNodeDetail.aboutToBeDeleted();
        this.__searchText.aboutToBeDeleted();
        SubscriberManager.Get().delete(this.id__());
        this.aboutToBeDeletedInternal();
    }
    private controller: web_webview.WebviewController;
    private __db: SynchedPropertySimpleOneWayPU<GraphDatabase>;
    get db() {
        return this.__db.get();
    }
    set db(newValue: GraphDatabase) {
        this.__db.set(newValue);
    }
    private __nodeCount: ObservedPropertySimplePU<number>;
    get nodeCount() {
        return this.__nodeCount.get();
    }
    set nodeCount(newValue: number) {
        this.__nodeCount.set(newValue);
    }
    private __edgeCount: ObservedPropertySimplePU<number>;
    get edgeCount() {
        return this.__edgeCount.get();
    }
    set edgeCount(newValue: number) {
        this.__edgeCount.set(newValue);
    }
    private __selectedNodeDetail: ObservedPropertyObjectPU<NodeDetailInfo | null>;
    get selectedNodeDetail() {
        return this.__selectedNodeDetail.get();
    }
    set selectedNodeDetail(newValue: NodeDetailInfo | null) {
        this.__selectedNodeDetail.set(newValue);
    }
    private __showNodeDetail: ObservedPropertySimplePU<boolean>;
    get showNodeDetail() {
        return this.__showNodeDetail.get();
    }
    set showNodeDetail(newValue: boolean) {
        this.__showNodeDetail.set(newValue);
    }
    private __searchText: ObservedPropertySimplePU<string>;
    get searchText() {
        return this.__searchText.get();
    }
    set searchText(newValue: string) {
        this.__searchText.set(newValue);
    }
    private graphService: GraphMemoryService;
    private bridge: NativeBridge;
    aboutToAppear() {
        this.graphService = new GraphMemoryService(this.db);
        this.bridge = new NativeBridge(this.controller, (): void => { this.pushGraphDataToWebView(); }, (nodeId: number, nodeName: string): void => { this.handleNodeClick(nodeId, nodeName); }, (query: string): void => { this.handleSearchFromWeb(query); });
    }
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
            if (!this.graphService)
                return;
            const detail: NodeDetailInfo | null = await this.graphService.getNodeDetail(nodeName);
            if (detail) {
                this.selectedNodeDetail = detail;
                this.showNodeDetail = true;
            }
        }
        catch (err) {
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
        const escapedValue = value.replace(/\\/g, '\\\\').replace(/'/g, "\\'").replace(/"/g, '\\"');
        const jsCode = `window.dispatchEvent(new MessageEvent('message', { data: { type: 'search_nodes', query: '${escapedValue}' } }));`;
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
                const jsCode: string = `window.loadGraphData(${JSON.stringify({ nodes: allNodes, edges: allEdges })});`;
                this.controller.runJavaScript(jsCode);
            }
            this.nodeCount = allNodes.length;
            this.edgeCount = allEdges.length;
        }
        catch (err) {
            Logger.error('pushGraphDataToWebView error: ' + JSON.stringify(err));
        }
    }
    initialRender() {
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Stack.create();
            Stack.width('100%');
            Stack.height('100%');
        }, Stack);
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            // WebView 显示 3D 星图
            Web.create({ src: { "id": 0, "type": 30000, params: ['graph.html'], "bundleName": "com.trulymem.app", "moduleName": "phone" }, controller: this.controller });
            // WebView 显示 3D 星图
            Web.javaScriptAccess(true);
            // WebView 显示 3D 星图
            Web.width('100%');
            // WebView 显示 3D 星图
            Web.height('100%');
            // WebView 显示 3D 星图
            Web.zoomAccess(true);
            // WebView 显示 3D 星图
            Web.onPageEnd(() => {
                this.pushGraphDataToWebView();
            });
            // WebView 显示 3D 星图
            Web.javaScriptProxy({
                object: this.bridge,
                name: 'nativeBridge',
                methodList: ['onNodeClick', 'onSearch'],
                asyncMethodList: ['requestGraphData'],
                controller: this.controller
            });
        }, Web);
        {
            this.observeComponentCreation2((elmtId, isInitialRender) => {
                if (isInitialRender) {
                    let componentCall = new 
                    // 搜索框
                    GraphNodeSearchBar(this, {
                        searchText: this.__searchText,
                        onSearchInput: (value: string): void => { this.onSearchInput(value); }
                    }, undefined, elmtId, () => { }, { page: "features/graph/src/main/ets/pages/GraphPage.ets", line: 189, col: 13 });
                    ViewPU.create(componentCall);
                    let paramsLambda = () => {
                        return {
                            searchText: this.searchText,
                            onSearchInput: (value: string): void => { this.onSearchInput(value); }
                        };
                    };
                    componentCall.paramsGenerator_ = paramsLambda;
                }
                else {
                    this.updateStateVarsOfChildByElmtId(elmtId, {});
                }
            }, { name: "GraphNodeSearchBar" });
        }
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            If.create();
            // 节点详情浮层
            if (this.showNodeDetail && this.selectedNodeDetail !== null) {
                this.ifElseBranchUpdateFunction(0, () => {
                    {
                        this.observeComponentCreation2((elmtId, isInitialRender) => {
                            if (isInitialRender) {
                                let componentCall = new NodeDetailPanel(this, {
                                    detail: this.selectedNodeDetail,
                                    onClose: (): void => { this.closeNodeDetail(); }
                                }, undefined, elmtId, () => { }, { page: "features/graph/src/main/ets/pages/GraphPage.ets", line: 196, col: 17 });
                                ViewPU.create(componentCall);
                                let paramsLambda = () => {
                                    return {
                                        detail: this.selectedNodeDetail,
                                        onClose: (): void => { this.closeNodeDetail(); }
                                    };
                                };
                                componentCall.paramsGenerator_ = paramsLambda;
                            }
                            else {
                                this.updateStateVarsOfChildByElmtId(elmtId, {
                                    detail: this.selectedNodeDetail
                                });
                            }
                        }, { name: "NodeDetailPanel" });
                    }
                });
            }
            else {
                this.ifElseBranchUpdateFunction(1, () => {
                });
            }
        }, If);
        If.pop();
        Stack.pop();
    }
    rerender() {
        this.updateDirtyElements();
    }
}
