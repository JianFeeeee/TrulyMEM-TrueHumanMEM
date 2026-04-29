import { MainPage } from './MainPage';
import { SettingsPage } from './SettingsPage';
import { GraphDatabase } from '../model/GraphDatabase';
import { ImmersiveTabNavigation } from '../components/ImmersiveTabNavigation';

@Entry
@Component
struct Index {
  @State currentIndex: number = 0;
  private db: GraphDatabase = new GraphDatabase();

  aboutToAppear() {
    this.db.init(getContext(this));
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
