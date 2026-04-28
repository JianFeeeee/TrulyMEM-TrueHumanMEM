if (!("finalizeConstruction" in ViewPU.prototype)) {
    Reflect.set(ViewPU.prototype, "finalizeConstruction", () => { });
}
interface MainPage_Params {
    db?: GraphDatabase;
}
import type { GraphDatabase } from '../model/GraphDatabase';
import { GraphPage } from "@normalized:N&&&entry/src/main/ets/pages/GraphPage&";
import { ChatPage } from "@normalized:N&&&entry/src/main/ets/pages/ChatPage&";
export class MainPage extends ViewPU {
    constructor(parent, params, __localStorage, elmtId = -1, paramsLambda = undefined, extraInfo) {
        super(parent, __localStorage, elmtId, extraInfo);
        if (typeof paramsLambda === "function") {
            this.paramsGenerator_ = paramsLambda;
        }
        this.__db = new SynchedPropertyObjectOneWayPU(params.db, this, "db");
        this.setInitiallyProvidedValue(params);
        this.finalizeConstruction();
    }
    setInitiallyProvidedValue(params: MainPage_Params) {
    }
    updateStateVars(params: MainPage_Params) {
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
    private __db: SynchedPropertySimpleOneWayPU<GraphDatabase>;
    get db() {
        return this.__db.get();
    }
    set db(newValue: GraphDatabase) {
        this.__db.set(newValue);
    }
    initialRender() {
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            GridRow.create({ columns: { sm: 1, md: 2, lg: 2 }, gutter: { x: 8, y: 8 } });
            GridRow.width('100%');
            GridRow.height('100%');
        }, GridRow);
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            GridCol.create({ span: { sm: 1, md: 1, lg: 1 } });
        }, GridCol);
        {
            this.observeComponentCreation2((elmtId, isInitialRender) => {
                if (isInitialRender) {
                    let componentCall = new GraphPage(this, { db: this.db }, undefined, elmtId, () => { }, { page: "entry/src/main/ets/pages/MainPage.ets", line: 12, col: 17 });
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
        GridCol.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            GridCol.create({ span: { sm: 1, md: 1, lg: 1 } });
        }, GridCol);
        {
            this.observeComponentCreation2((elmtId, isInitialRender) => {
                if (isInitialRender) {
                    let componentCall = new ChatPage(this, { db: this.db }, undefined, elmtId, () => { }, { page: "entry/src/main/ets/pages/MainPage.ets", line: 15, col: 17 });
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
        GridCol.pop();
        GridRow.pop();
    }
    rerender() {
        this.updateDirtyElements();
    }
}
