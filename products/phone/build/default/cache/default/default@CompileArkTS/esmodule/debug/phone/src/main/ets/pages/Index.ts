if (!("finalizeConstruction" in ViewPU.prototype)) {
    Reflect.set(ViewPU.prototype, "finalizeConstruction", () => { });
}
interface Index_Params {
    db?: GraphDatabase;
    displayCallback?: Callback<number>;
}
import { GraphDatabase } from "@normalized:N&&&@ohos/common/Index&1.0.0";
import { MainPage } from "@normalized:N&&&@ohos/phone/src/main/ets/pages/MainPage&";
import display from "@ohos:display";
class Index extends ViewPU {
    constructor(parent, params, __localStorage, elmtId = -1, paramsLambda = undefined, extraInfo) {
        super(parent, __localStorage, elmtId, extraInfo);
        if (typeof paramsLambda === "function") {
            this.paramsGenerator_ = paramsLambda;
        }
        this.db = new GraphDatabase();
        this.displayCallback = undefined;
        this.setInitiallyProvidedValue(params);
        this.finalizeConstruction();
    }
    setInitiallyProvidedValue(params: Index_Params) {
        if (params.db !== undefined) {
            this.db = params.db;
        }
        if (params.displayCallback !== undefined) {
            this.displayCallback = params.displayCallback;
        }
    }
    updateStateVars(params: Index_Params) {
    }
    purgeVariableDependenciesOnElmtId(rmElmtId) {
    }
    aboutToBeDeleted() {
        SubscriberManager.Get().delete(this.id__());
        this.aboutToBeDeletedInternal();
    }
    private db: GraphDatabase;
    private displayCallback?: Callback<number>;
    aboutToAppear() {
        const ctx = this.getUIContext()?.getHostContext();
        if (ctx) {
            this.db.init(ctx);
        }
        // TODO: display.on('change') API 在 API 23 中已废弃，应替换为窗口尺寸监听
        // 当前保留以兼容旧代码，后续应使用 window.on('windowSizeChange') 或断点系统替代
        // try {
        //   this.displayCallback = (size: number): void => { };
        //   display.on('change', this.displayCallback);
        // } catch (e) {
        //   Logger.error('display.on error: ' + JSON.stringify(e));
        // }
    }
    aboutToDisappear() {
        if (this.displayCallback) {
            display.off('change', this.displayCallback);
        }
    }
    initialRender() {
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Column.create();
            Column.width('100%');
            Column.height('100%');
        }, Column);
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            __Common__.create();
            __Common__.width('100%');
            __Common__.height('100%');
        }, __Common__);
        {
            this.observeComponentCreation2((elmtId, isInitialRender) => {
                if (isInitialRender) {
                    let componentCall = new MainPage(this, { db: this.db }, undefined, elmtId, () => { }, { page: "products/phone/src/main/ets/pages/Index.ets", line: 34, col: 7 });
                    ViewPU.create(componentCall);
                    let paramsLambda = () => {
                        return {
                            db: this.db
                        };
                    };
                    componentCall.paramsGenerator_ = paramsLambda;
                }
                else {
                    this.updateStateVarsOfChildByElmtId(elmtId, {
                        db: this.db
                    });
                }
            }, { name: "MainPage" });
        }
        __Common__.pop();
        Column.pop();
    }
    rerender() {
        this.updateDirtyElements();
    }
    static getEntryName(): string {
        return "Index";
    }
}
registerNamedRoute(() => new Index(undefined, {}), "", { bundleName: "com.trulymem.app", moduleName: "phone", pagePath: "pages/Index", pageFullPath: "products/phone/src/main/ets/pages/Index", integratedHsp: "false", moduleType: "followWithHap" });
