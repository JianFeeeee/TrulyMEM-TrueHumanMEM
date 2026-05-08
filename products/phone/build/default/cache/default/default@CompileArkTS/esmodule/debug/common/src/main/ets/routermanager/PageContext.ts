import { defaultLogger } from "@normalized:N&&&@ohos/common/src/main/ets/util/Logger&1.0.0";
import type { BusinessError } from "@ohos:base";
export interface RouterParam {
    routerName: string;
    param?: object;
}
export interface IPageContext {
    openPage(data: RouterParam, animated?: boolean): void;
    popPage(animated?: boolean): void;
    replacePage(data: RouterParam, animated?: boolean): void;
}
export class PageContext implements IPageContext {
    private readonly pathStack: NavPathStack;
    constructor() {
        this.pathStack = new NavPathStack();
    }
    public get navPathStack(): NavPathStack {
        return this.pathStack;
    }
    public replacePage(data: RouterParam, animated: boolean = true): void {
        try {
            this.pathStack.replacePath({ name: data.routerName, param: data.param }, animated);
        }
        catch (err) {
            const errMsg = (err as BusinessError).message || JSON.stringify(err);
            defaultLogger.error('replacePage: ' + data.routerName + ' failed. ' + errMsg);
        }
    }
    public openPage(data: RouterParam, animated: boolean = true): void {
        try {
            this.pathStack.pushPath({ name: data.routerName, param: data.param }, animated);
        }
        catch (err) {
            const errMsg = (err as BusinessError).message || JSON.stringify(err);
            defaultLogger.error('openPage: ' + data.routerName + ' failed. ' + errMsg);
        }
    }
    public popPage(animated: boolean = true): void {
        try {
            this.pathStack.pop(animated);
        }
        catch (err) {
            const errMsg = (err as BusinessError).message || JSON.stringify(err);
            defaultLogger.error('popPage failed. ' + errMsg);
        }
    }
    public popPageByIndex(index: number, animated: boolean = true): void {
        this.pathStack.popToIndex(index, animated);
    }
    public clear(animated: boolean = true): void {
        this.pathStack.clear(animated);
    }
}
