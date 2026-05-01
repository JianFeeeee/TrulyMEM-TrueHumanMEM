import { defaultLogger } from '../util/Logger';

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
    } catch (err) {
      defaultLogger.error('replacePage: ' + data.routerName + ' failed. ' + err.code + ' ' + err.message);
    }
  }

  public openPage(data: RouterParam, animated: boolean = true): void {
    try {
      this.pathStack.pushPath({ name: data.routerName, param: data.param }, animated);
    } catch (err) {
      defaultLogger.error('openPage: ' + data.routerName + ' failed. ' + err.code + ' ' + err.message);
    }
  }

  public popPage(animated: boolean = true): void {
    try {
      this.pathStack.pop(animated);
    } catch (err) {
      defaultLogger.error('popPage failed. ' + err.code + ' ' + err.message);
    }
  }

  public popPageByIndex(index: number, animated: boolean = true): void {
    this.pathStack.popToIndex(index, animated);
  }

  public clear(animated: boolean = true): void {
    this.pathStack.clear(animated);
  }
}
