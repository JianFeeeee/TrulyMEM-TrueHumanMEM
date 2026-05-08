if (!("finalizeConstruction" in ViewPU.prototype)) {
    Reflect.set(ViewPU.prototype, "finalizeConstruction", () => { });
}
interface MainPage_Params {
    db?: GraphDatabase;
    isWide?: boolean;
    currentIndex?: number;
}
import { GraphDatabase, Logger, ImmersiveTabNavigation } from "@normalized:N&&&@ohos/common/Index&1.0.0";
import { GraphPage } from "@normalized:N&&&@ohos/graph/Index&1.0.0";
import { ChatPage } from "@normalized:N&&&@ohos/chat/Index&1.0.0";
import { SettingsPage } from "@normalized:N&&&@ohos/settings/Index&1.0.0";
import display from "@ohos:display";
export function MainPageBuilder(parent = null) {
    {
        (parent ? parent : this).observeComponentCreation2((elmtId, isInitialRender) => {
            if (isInitialRender) {
                let componentCall = new MainPage(parent ? parent : this, { db: new GraphDatabase() }, undefined, elmtId, () => { }, { page: "products/phone/src/main/ets/pages/MainPage.ets", line: 10, col: 3 });
                ViewPU.create(componentCall);
                let paramsLambda = () => {
                    return {
                        db: new GraphDatabase()
                    };
                };
                componentCall.paramsGenerator_ = paramsLambda;
            }
            else {
                (parent ? parent : this).updateStateVarsOfChildByElmtId(elmtId, {
                    db: new GraphDatabase()
                });
            }
        }, { name: "MainPage" });
    }
}
export class MainPage extends ViewPU {
    constructor(parent, params, __localStorage, elmtId = -1, paramsLambda = undefined, extraInfo) {
        super(parent, __localStorage, elmtId, extraInfo);
        if (typeof paramsLambda === "function") {
            this.paramsGenerator_ = paramsLambda;
        }
        this.__db = new SynchedPropertyObjectOneWayPU(params.db, this, "db");
        this.__isWide = new ObservedPropertySimplePU(false, this, "isWide");
        this.__currentIndex = new ObservedPropertySimplePU(0, this, "currentIndex");
        this.setInitiallyProvidedValue(params);
        this.finalizeConstruction();
    }
    setInitiallyProvidedValue(params: MainPage_Params) {
        if (params.isWide !== undefined) {
            this.isWide = params.isWide;
        }
        if (params.currentIndex !== undefined) {
            this.currentIndex = params.currentIndex;
        }
    }
    updateStateVars(params: MainPage_Params) {
        this.__db.reset(params.db);
    }
    purgeVariableDependenciesOnElmtId(rmElmtId) {
        this.__db.purgeDependencyOnElmtId(rmElmtId);
        this.__isWide.purgeDependencyOnElmtId(rmElmtId);
        this.__currentIndex.purgeDependencyOnElmtId(rmElmtId);
    }
    aboutToBeDeleted() {
        this.__db.aboutToBeDeleted();
        this.__isWide.aboutToBeDeleted();
        this.__currentIndex.aboutToBeDeleted();
        SubscriberManager.Get().delete(this.id__());
        this.aboutToBeDeletedInternal();
    }
    private __db: SynchedPropertySimpleOneWayPU<GraphDatabase>;
    get db() {
        return this.__db.get();
    }
    set db(newValue: GraphDatabase) {
        this.__db.set(newValue);
    }
    private __isWide: ObservedPropertySimplePU<boolean>;
    get isWide() {
        return this.__isWide.get();
    }
    set isWide(newValue: boolean) {
        this.__isWide.set(newValue);
    }
    private __currentIndex: ObservedPropertySimplePU<number>;
    get currentIndex() {
        return this.__currentIndex.get();
    }
    set currentIndex(newValue: number) {
        this.__currentIndex.set(newValue);
    }
    aboutToAppear() {
        this.updateBreakpoint();
        try {
            display.on('change', () => { this.updateBreakpoint(); });
        }
        catch (e) {
            Logger.error('display.on error: ' + JSON.stringify(e));
        }
    }
    private updateBreakpoint(): void {
        try {
            const defaultWindow = display.getDefaultDisplaySync();
            this.isWide = defaultWindow.width > 520;
        }
        catch (e) {
            Logger.error('updateBreakpoint error: ' + JSON.stringify(e));
        }
    }
    TrulyMEMContent(parent = null) {
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            If.create();
            if (this.isWide) {
                this.ifElseBranchUpdateFunction(0, () => {
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        Row.create();
                        Row.width('100%');
                        Row.height('100%');
                        Row.padding(4);
                        Row.backgroundColor('#1A1B2E');
                    }, Row);
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        __Common__.create();
                        __Common__.layoutWeight(1);
                        __Common__.height('100%');
                        __Common__.clip(true);
                        __Common__.borderRadius(12);
                        __Common__.margin({ left: 4, right: 2 });
                    }, __Common__);
                    {
                        this.observeComponentCreation2((elmtId, isInitialRender) => {
                            if (isInitialRender) {
                                let componentCall = new GraphPage(this, { db: this.db }, undefined, elmtId, () => { }, { page: "products/phone/src/main/ets/pages/MainPage.ets", line: 41, col: 9 });
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
                        }, { name: "GraphPage" });
                    }
                    __Common__.pop();
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        __Common__.create();
                        __Common__.width(380);
                        __Common__.height('100%');
                        __Common__.clip(true);
                        __Common__.borderRadius(12);
                        __Common__.margin({ left: 2, right: 4 });
                    }, __Common__);
                    {
                        this.observeComponentCreation2((elmtId, isInitialRender) => {
                            if (isInitialRender) {
                                let componentCall = new ChatPage(this, { db: this.db }, undefined, elmtId, () => { }, { page: "products/phone/src/main/ets/pages/MainPage.ets", line: 48, col: 9 });
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
                        }, { name: "ChatPage" });
                    }
                    __Common__.pop();
                    Row.pop();
                });
            }
            else {
                this.ifElseBranchUpdateFunction(1, () => {
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        Column.create();
                        Column.width('100%');
                        Column.height('100%');
                        Column.padding(2);
                        Column.backgroundColor('#1A1B2E');
                    }, Column);
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        Stack.create();
                        Stack.height('55%');
                        Stack.width('100%');
                        Stack.clip(true);
                        Stack.borderRadius(12);
                        Stack.margin({ top: 2, left: 4, right: 4, bottom: 2 });
                    }, Stack);
                    {
                        this.observeComponentCreation2((elmtId, isInitialRender) => {
                            if (isInitialRender) {
                                let componentCall = new GraphPage(this, { db: this.db }, undefined, elmtId, () => { }, { page: "products/phone/src/main/ets/pages/MainPage.ets", line: 61, col: 19 });
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
                        }, { name: "GraphPage" });
                    }
                    Stack.pop();
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        Stack.create();
                        Stack.height('45%');
                        Stack.width('100%');
                        Stack.clip(true);
                        Stack.borderRadius(12);
                        Stack.margin({ top: 2, left: 4, right: 4, bottom: 2 });
                    }, Stack);
                    {
                        this.observeComponentCreation2((elmtId, isInitialRender) => {
                            if (isInitialRender) {
                                let componentCall = new ChatPage(this, { db: this.db }, undefined, elmtId, () => { }, { page: "products/phone/src/main/ets/pages/MainPage.ets", line: 68, col: 19 });
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
                        }, { name: "ChatPage" });
                    }
                    Stack.pop();
                    Column.pop();
                });
            }
        }, If);
        If.pop();
    }
    SettingsContent(parent = null) {
        {
            this.observeComponentCreation2((elmtId, isInitialRender) => {
                if (isInitialRender) {
                    let componentCall = new SettingsPage(this, {}, undefined, elmtId, () => { }, { page: "products/phone/src/main/ets/pages/MainPage.ets", line: 84, col: 5 });
                    ViewPU.create(componentCall);
                    let paramsLambda = () => {
                        return {};
                    };
                    componentCall.paramsGenerator_ = paramsLambda;
                }
                else {
                    this.updateStateVarsOfChildByElmtId(elmtId, {});
                }
            }, { name: "SettingsPage" });
        }
    }
    TabContentBuilder(parent = null) {
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            If.create();
            if (this.currentIndex === 0) {
                this.ifElseBranchUpdateFunction(0, () => {
                    this.TrulyMEMContent.bind(this)();
                });
            }
            else {
                this.ifElseBranchUpdateFunction(1, () => {
                    this.SettingsContent.bind(this)();
                });
            }
        }, If);
        If.pop();
    }
    initialRender() {
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            __Common__.create();
            __Common__.width('100%');
            __Common__.height('100%');
        }, __Common__);
        {
            this.observeComponentCreation2((elmtId, isInitialRender) => {
                if (isInitialRender) {
                    let componentCall = new ImmersiveTabNavigation(this, {
                        contentBuilder: this.TabContentBuilder,
                        onTabChange: (index: number) => {
                            this.currentIndex = index;
                        }
                    }, undefined, elmtId, () => { }, { page: "products/phone/src/main/ets/pages/MainPage.ets", line: 97, col: 5 });
                    ViewPU.create(componentCall);
                    let paramsLambda = () => {
                        return {
                            contentBuilder: this.TabContentBuilder,
                            onTabChange: (index: number) => {
                                this.currentIndex = index;
                            }
                        };
                    };
                    componentCall.paramsGenerator_ = paramsLambda;
                }
                else {
                    this.updateStateVarsOfChildByElmtId(elmtId, {});
                }
            }, { name: "ImmersiveTabNavigation" });
        }
        __Common__.pop();
    }
    rerender() {
        this.updateDirtyElements();
    }
}
(function () {
    if (typeof NavigationBuilderRegister === "function") {
        NavigationBuilderRegister("MainPage", wrapBuilder(MainPageBuilder));
    }
})();
