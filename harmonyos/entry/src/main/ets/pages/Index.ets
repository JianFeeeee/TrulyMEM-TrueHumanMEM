import { MainPage } from './MainPage';
import { SettingsPage } from './SettingsPage';
import { GraphDatabase } from '../model/GraphDatabase';

@Entry
@Component
struct Index {
    @State currentIndex: number = 0;
    private db: GraphDatabase = new GraphDatabase();

    aboutToAppear() {
        this.db.init(getContext(this));
    }

    build() {
        Column() {
            Tabs({ index: this.currentIndex, barPosition: BarPosition.End }) {
                TabContent() {
                    MainPage({ db: this.db })
                }
                .tabBar('🌌 TrulyMEM')

                TabContent() {
                    SettingsPage()
                }
                .tabBar('⚙ 设置')
            }
            .width('100%')
            .height('100%')
            .onChange((index: number) => { this.currentIndex = index; })
        }
        .width('100%')
        .height('100%')
    }
}
