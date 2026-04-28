import { GraphDatabase } from '../model/GraphDatabase';
import { GraphPage } from './GraphPage';
import { ChatPage } from './ChatPage';

@Component
export struct MainPage {
    @Prop db: GraphDatabase;

    build() {
        GridRow({ columns: { sm: 1, md: 2, lg: 2 }, gutter: { x: 8, y: 8 } }) {
            GridCol({ span: { sm: 1, md: 1, lg: 1 } }) {
                GraphPage({ db: this.db })
            }
            GridCol({ span: { sm: 1, md: 1, lg: 1 } }) {
                ChatPage({ db: this.db })
            }
        }
        .width('100%')
        .height('100%')
    }
}
