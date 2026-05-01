    import { GraphDatabase, Logger } from '@ohos/common';
import { MainPage } from './MainPage';
import display from '@ohos.display';

@Entry
@Component
struct Index {
  private db: GraphDatabase = new GraphDatabase();
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

  build() {
    Column() {
      MainPage({ db: this.db })
        .width('100%')
        .height('100%')
    }
    .width('100%')
    .height('100%')
  }
}
