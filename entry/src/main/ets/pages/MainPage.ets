import { GraphDatabase } from '../model/GraphDatabase';
import { GraphPage } from './GraphPage';
import { ChatPage } from './ChatPage';
import display from '@ohos.display';

@Component
export struct MainPage {
    @Prop db: GraphDatabase;
    @State isWide: boolean = false;

    aboutToAppear() {
        this.updateBreakpoint();
        try {
            display.on('change', () => {
                this.updateBreakpoint();
            });
        } catch (e) {
            console.error('display.on error: ' + JSON.stringify(e));
        }
    }

    private updateBreakpoint(): void {
        try {
            const defaultWindow = display.getDefaultDisplaySync();
            this.isWide = defaultWindow.width > 520;
        } catch (e) {
            console.error('updateBreakpoint error: ' + JSON.stringify(e));
        }
    }

    build() {
        if (this.isWide) {
            // ======== 宽屏模式（>520px）：左侧星图 + 右侧聊天 ========
            Row() {
                GraphPage({ db: this.db })
                    .layoutWeight(1)
                    .height('100%')
                    .clip(true)
                    .borderRadius(12)
                    .margin({ left: 4, right: 2 })

                ChatPage({ db: this.db })
                    .width(380)
                    .height('100%')
                    .clip(true)
                    .borderRadius(12)
                    .margin({ left: 2, right: 4 })
            }
            .width('100%')
            .height('100%')
            .padding(4)
            .backgroundColor('#1A1B2E')
            .backgroundBlurStyle(BlurStyle.Regular)
        } else {
            // ======== 窄屏模式（≤520px）：上方星图(55%) + 下方聊天(45%) ========
            Column() {
                Stack() {
                    GraphPage({ db: this.db })
                }
                .height('55%')
                .width('100%')
                .clip(true)
                .borderRadius(12)
                .margin({ top: 2, left: 4, right: 4, bottom: 2 })

                Stack() {
                    ChatPage({ db: this.db })
                }
                .height('45%')
                .width('100%')
                .clip(true)
                .borderRadius(12)
                .margin({ top: 2, left: 4, right: 4, bottom: 2 })
            }
            .width('100%')
            .height('100%')
            .padding(2)
            .backgroundColor('#1A1B2E')
            .backgroundBlurStyle(BlurStyle.Regular)
        }
    }
}
