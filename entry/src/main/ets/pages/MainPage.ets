import { GraphDatabase } from '../model/GraphDatabase';
import { GraphPage } from './GraphPage';
import { ChatPage } from './ChatPage';

@Component
export struct MainPage {
    @Prop db: GraphDatabase;

    build() {
        GridRow({ columns: { sm: 1, md: 2, lg: 2 }, gutter: { x: 8, y: 8 } }) {
            GridCol({ span: { sm: 1, md: 1, lg: 1 } }) {
                Stack() {
                    GraphPage({ db: this.db })
                }
                .backgroundColor('rgba(255,255,255,0.05)')
                .borderRadius(12)
                .backgroundBlurStyle(BlurStyle.Thin)
                .width('100%')
                .height('100%')
            }

            GridCol({ span: { sm: 1, md: 1, lg: 1 } }) {
                Stack() {
                    ChatPage({ db: this.db })
                }
                .backgroundColor('rgba(255,255,255,0.05)')
                .borderRadius(12)
                .backgroundBlurStyle(BlurStyle.Thin)
                .width('100%')
                .height('100%')
            }
        }
        .width('100%')
        .height('100%')
        .backgroundColor('#1A1B2E')
        .backgroundBlurStyle(BlurStyle.Regular)
    }
}
