import { MainPage } from './MainPage';
import { SettingsPage } from './SettingsPage';
import { GraphDatabase } from '../model/GraphDatabase';
import { ImmersiveTabNavigation } from '../components/ImmersiveTabNavigation';
import display from '@ohos.display';

@Entry
@Component
struct Index {
  @State currentIndex: number = 0;
  private db: GraphDatabase = new GraphDatabase();
  private displayCallback?: Callback<number>;

  aboutToAppear() {
    this.db.init(getContext(this));
  }

  aboutToDisappear() {
    if (this.displayCallback) {
      display.off('change', this.displayCallback);
    }
  }

  @Builder
  tabContentBuilder() {
    Column() {
      if (this.currentIndex === 0) {
        MainPage({ db: this.db })
      } else {
        SettingsPage()
      }
    }
    .width('100%')
    .height('100%')
  }

  build() {
    Stack() {
      ImmersiveTabNavigation({
        currentIndex: this.currentIndex,
        onTabChange: (index: number): void => { this.currentIndex = index; },
        contentBuilder: (): void => { this.tabContentBuilder(); }
      })
    }
    .width('100%')
    .height('100%')
  }
}
