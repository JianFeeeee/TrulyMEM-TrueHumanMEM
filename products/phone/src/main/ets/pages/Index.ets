import { GraphDatabase } from '@ohos/common';
import { MainPage } from './MainPage';
import display from '@ohos.display';

@Entry
@Component
struct Index {
  private db: GraphDatabase = new GraphDatabase();
  private displayCallback?: Callback<number>;

  aboutToAppear() {
    this.db.init(getContext(this));
    try {
      this.displayCallback = (size: number): void => {
      };
      display.on('change', this.displayCallback);
    } catch (e) {
      console.error('display.on error: ' + JSON.stringify(e));
    }
  }

  aboutToDisappear() {
    if (this.displayCallback) {
      display.off('change', this.displayCallback);
    }
  }

  build() {
    MainPage({ db: this.db }).width('100%').height('100%');
  }
}
