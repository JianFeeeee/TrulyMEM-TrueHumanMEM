if (!("finalizeConstruction" in ViewPU.prototype)) {
    Reflect.set(ViewPU.prototype, "finalizeConstruction", () => { });
}
interface GraphWebView_Params {
    controller?: web_webview.WebviewController;
    bridge?: NativeBridge;
    onPageEnd?: () => void;
}
interface NodeDetailPanel_Params {
    detail?: NodeDetailInfo;
    onClose?: () => void;
}
interface GraphNodeSearchBar_Params {
    searchText?: string;
    onSearchInput?: (value: string) => void;
}
import web_webview from "@ohos:web.webview";
import { Logger } from "@normalized:N&&&@ohos/common/Index&1.0.0";
import type { GraphDatabase, RecallEntity, ConnectionItem, NodeDetailInfo } from "@normalized:N&&&@ohos/common/Index&1.0.0";
export class GraphNodeSearchBar extends ViewPU {
    constructor(parent, params, __localStorage, elmtId = -1, paramsLambda = undefined, extraInfo) {
        super(parent, __localStorage, elmtId, extraInfo);
        if (typeof paramsLambda === "function") {
            this.paramsGenerator_ = paramsLambda;
        }
        this.__searchText = new SynchedPropertySimpleTwoWayPU(params.searchText, this, "searchText");
        this.onSearchInput = undefined;
        this.setInitiallyProvidedValue(params);
        this.finalizeConstruction();
    }
    setInitiallyProvidedValue(params: GraphNodeSearchBar_Params) {
        if (params.onSearchInput !== undefined) {
            this.onSearchInput = params.onSearchInput;
        }
    }
    updateStateVars(params: GraphNodeSearchBar_Params) {
    }
    purgeVariableDependenciesOnElmtId(rmElmtId) {
        this.__searchText.purgeDependencyOnElmtId(rmElmtId);
    }
    aboutToBeDeleted() {
        this.__searchText.aboutToBeDeleted();
        SubscriberManager.Get().delete(this.id__());
        this.aboutToBeDeletedInternal();
    }
    private __searchText: SynchedPropertySimpleTwoWayPU<string>;
    get searchText() {
        return this.__searchText.get();
    }
    set searchText(newValue: string) {
        this.__searchText.set(newValue);
    }
    private onSearchInput?: (value: string) => void;
    initialRender() {
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Column.create();
            Column.width('100%');
            Column.position({ x: 0, y: 0 });
            Column.zIndex(10);
        }, Column);
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            TextInput.create({ placeholder: '搜索节点...', text: this.searchText });
            TextInput.width('80%');
            TextInput.height(40);
            TextInput.backgroundColor('rgba(10, 10, 26, 0.8)');
            TextInput.fontColor('#ffffff');
            TextInput.placeholderColor('#666688');
            TextInput.borderRadius(8);
            TextInput.border({ width: 1, color: 'rgba(100, 100, 255, 0.3)' });
            TextInput.margin({ top: 20 });
            TextInput.onChange((value: string) => {
                this.onSearchInput?.(value);
            });
        }, TextInput);
        Column.pop();
    }
    rerender() {
        this.updateDirtyElements();
    }
}
export class NodeDetailPanel extends ViewPU {
    constructor(parent, params, __localStorage, elmtId = -1, paramsLambda = undefined, extraInfo) {
        super(parent, __localStorage, elmtId, extraInfo);
        if (typeof paramsLambda === "function") {
            this.paramsGenerator_ = paramsLambda;
        }
        this.__detail = new SynchedPropertyObjectOneWayPU(params.detail, this, "detail");
        this.onClose = undefined;
        this.setInitiallyProvidedValue(params);
        this.finalizeConstruction();
    }
    setInitiallyProvidedValue(params: NodeDetailPanel_Params) {
        if (params.onClose !== undefined) {
            this.onClose = params.onClose;
        }
    }
    updateStateVars(params: NodeDetailPanel_Params) {
        this.__detail.reset(params.detail);
    }
    purgeVariableDependenciesOnElmtId(rmElmtId) {
        this.__detail.purgeDependencyOnElmtId(rmElmtId);
    }
    aboutToBeDeleted() {
        this.__detail.aboutToBeDeleted();
        SubscriberManager.Get().delete(this.id__());
        this.aboutToBeDeletedInternal();
    }
    private __detail: SynchedPropertySimpleOneWayPU<NodeDetailInfo>;
    get detail() {
        return this.__detail.get();
    }
    set detail(newValue: NodeDetailInfo) {
        this.__detail.set(newValue);
    }
    private onClose?: () => void;
    initialRender() {
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Column.create();
            Column.width('100%');
            Column.height('100%');
            Column.backgroundColor('rgba(0, 0, 0, 0.5)');
            Column.justifyContent(FlexAlign.Center);
            Column.alignItems(HorizontalAlign.Center);
            Column.zIndex(20);
        }, Column);
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Column.create();
            Column.padding(20);
            Column.backgroundColor('rgba(10, 10, 26, 0.95)');
            Column.borderRadius(12);
            Column.border({ width: 1, color: 'rgba(100, 100, 255, 0.3)' });
            Column.width(300);
        }, Column);
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Text.create(this.detail.name);
            Text.fontSize(18);
            Text.fontColor('#44ff88');
            Text.fontWeight(FontWeight.Bold);
            Text.margin({ bottom: 10 });
        }, Text);
        Text.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Text.create('类型: ' + this.detail.type);
            Text.fontSize(14);
            Text.fontColor('#aaaacc');
        }, Text);
        Text.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Text.create('提及次数: ' + this.detail.mention_count);
            Text.fontSize(14);
            Text.fontColor('#aaaacc');
        }, Text);
        Text.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Text.create('连接数: ' + this.detail.connection_count);
            Text.fontSize(14);
            Text.fontColor('#aaaacc');
        }, Text);
        Text.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            If.create();
            if (this.detail.connections && this.detail.connections.length > 0) {
                this.ifElseBranchUpdateFunction(0, () => {
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        Text.create('连接关系:');
                        Text.fontSize(14);
                        Text.fontColor('#8888aa');
                        Text.margin({ top: 10, bottom: 5 });
                    }, Text);
                    Text.pop();
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        List.create();
                        List.height(100);
                    }, List);
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        ForEach.create();
                        const forEachItemGenFunction = _item => {
                            const conn = _item;
                            {
                                const itemCreation = (elmtId, isInitialRender) => {
                                    ViewStackProcessor.StartGetAccessRecordingFor(elmtId);
                                    ListItem.create(deepRenderFunction, true);
                                    if (!isInitialRender) {
                                        ListItem.pop();
                                    }
                                    ViewStackProcessor.StopGetAccessRecording();
                                };
                                const itemCreation2 = (elmtId, isInitialRender) => {
                                    ListItem.create(deepRenderFunction, true);
                                };
                                const deepRenderFunction = (elmtId, isInitialRender) => {
                                    itemCreation(elmtId, isInitialRender);
                                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                                        Text.create(conn.type + ': ' + conn.target_name);
                                        Text.fontSize(12);
                                        Text.fontColor('#aaaacc');
                                    }, Text);
                                    Text.pop();
                                    ListItem.pop();
                                };
                                this.observeComponentCreation2(itemCreation2, ListItem);
                                ListItem.pop();
                            }
                        };
                        this.forEachUpdateFunction(elmtId, this.detail.connections, forEachItemGenFunction);
                    }, ForEach);
                    ForEach.pop();
                    List.pop();
                });
            }
            else {
                this.ifElseBranchUpdateFunction(1, () => {
                });
            }
        }, If);
        If.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Button.createWithLabel('关闭');
            Button.width(80);
            Button.height(30);
            Button.margin({ top: 15 });
            Button.backgroundColor('rgba(100, 100, 255, 0.3)');
            Button.fontColor('#ffffff');
            Button.onClick(() => {
                this.onClose?.();
            });
        }, Button);
        Button.pop();
        Column.pop();
        Column.pop();
    }
    rerender() {
        this.updateDirtyElements();
    }
}
export class GraphWebView extends ViewPU {
    constructor(parent, params, __localStorage, elmtId = -1, paramsLambda = undefined, extraInfo) {
        super(parent, __localStorage, elmtId, extraInfo);
        if (typeof paramsLambda === "function") {
            this.paramsGenerator_ = paramsLambda;
        }
        this.controller = new web_webview.WebviewController();
        this.bridge = undefined;
        this.onPageEnd = undefined;
        this.setInitiallyProvidedValue(params);
        this.finalizeConstruction();
    }
    setInitiallyProvidedValue(params: GraphWebView_Params) {
        if (params.controller !== undefined) {
            this.controller = params.controller;
        }
        if (params.bridge !== undefined) {
            this.bridge = params.bridge;
        }
        if (params.onPageEnd !== undefined) {
            this.onPageEnd = params.onPageEnd;
        }
    }
    updateStateVars(params: GraphWebView_Params) {
    }
    purgeVariableDependenciesOnElmtId(rmElmtId) {
    }
    aboutToBeDeleted() {
        SubscriberManager.Get().delete(this.id__());
        this.aboutToBeDeletedInternal();
    }
    private controller: web_webview.WebviewController;
    private bridge?: NativeBridge;
    private onPageEnd?: () => void;
    getController(): web_webview.WebviewController {
        return this.controller;
    }
    setBridge(bridge: NativeBridge): void {
        this.bridge = bridge;
    }
    initialRender() {
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Web.create({ src: { "id": 0, "type": 30000, params: ['graph.html'], "bundleName": "com.trulymem.app", "moduleName": "phone" }, controller: this.controller });
            Web.javaScriptAccess(true);
            Web.width('100%');
            Web.height('100%');
            Web.zoomAccess(true);
            Web.onPageEnd(() => {
                this.onPageEnd?.();
            });
            Web.javaScriptProxy({
                object: this.bridge,
                name: 'nativeBridge',
                methodList: ['onNodeClick', 'onSearch'],
                asyncMethodList: ['requestGraphData'],
                controller: this.controller
            });
        }, Web);
    }
    rerender() {
        this.updateDirtyElements();
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
    constructor(controller: web_webview.WebviewController, onRequestGraphData: () => void, onNodeClickCallback: (nodeId: number, nodeName: string) => void, onSearchCallback: (query: string) => void) {
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
