if (!("finalizeConstruction" in ViewPU.prototype)) {
    Reflect.set(ViewPU.prototype, "finalizeConstruction", () => { });
}
interface GraphPage_Params {
    controller?: web_webview.WebviewController;
    db?: GraphDatabase;
}
import web_webview from "@ohos:web.webview";
import type { GraphDatabase } from '../model/GraphDatabase';
export class GraphPage extends ViewPU {
    constructor(parent, params, __localStorage, elmtId = -1, paramsLambda = undefined, extraInfo) {
        super(parent, __localStorage, elmtId, extraInfo);
        if (typeof paramsLambda === "function") {
            this.paramsGenerator_ = paramsLambda;
        }
        this.controller = new web_webview.WebviewController();
        this.__db = new SynchedPropertyObjectOneWayPU(params.db, this, "db");
        this.setInitiallyProvidedValue(params);
        this.finalizeConstruction();
    }
    setInitiallyProvidedValue(params: GraphPage_Params) {
        if (params.controller !== undefined) {
            this.controller = params.controller;
        }
    }
    updateStateVars(params: GraphPage_Params) {
        this.__db.reset(params.db);
    }
    purgeVariableDependenciesOnElmtId(rmElmtId) {
        this.__db.purgeDependencyOnElmtId(rmElmtId);
    }
    aboutToBeDeleted() {
        this.__db.aboutToBeDeleted();
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
    initialRender() {
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Column.create();
            Column.width('100%');
            Column.height('100%');
            Column.onAppear(() => {
                this.controller.refresh();
            });
        }, Column);
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Web.create({ src: { "id": 0, "type": 30000, params: ['graph.html'], "bundleName": "com.trulymem.app", "moduleName": "entry" }, controller: this.controller });
            Web.javaScriptAccess(true);
            Web.width('100%');
            Web.height('100%');
        }, Web);
        Column.pop();
    }
    rerender() {
        this.updateDirtyElements();
    }
}
