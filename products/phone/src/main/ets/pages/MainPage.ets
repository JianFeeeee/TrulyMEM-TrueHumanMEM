import { GraphDatabase } from '@ohos/common';
import { GraphPage } from '@ohos/graph';
import { ChatPage } from '@ohos/chat';
import { SettingsPage } from '@ohos/settings';
import display from '@ohos.display';

@Component
export struct MainPage {
    @Prop db: GraphDatabase;
    @State isWide: boolean = false;
    @State currentIndex: number = 0;
    private tabController: TabsController = new TabsController();

    aboutToAppear() {
        this.updateBreakpoint();
        try {
            display.on('change', () => { this.updateBreakpoint(); });
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

    @Builder
    TabContentsBuilder() {
        TabContent() {
            if (this.isWide) {
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
            } else {
                Column() {
                    Stack() { GraphPage({ db: this.db }) }
                        .height('55%')
                        .width('100%')
                        .clip(true)
                        .borderRadius(12)
                        .margin({ top: 2, left: 4, right: 4, bottom: 2 })

                    Stack() { ChatPage({ db: this.db }) }
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
            }
        }
        .tabBar(this.bottomTabBarStyle('TrulyMEM', '\ue8b6'))

        TabContent() {
            SettingsPage()
        }
        .tabBar(this.bottomTabBarStyle('设置', '\ue8b8'))
    }

    private bottomTabBarStyle(title: string, icon: string): BottomTabBarStyle {
        return new BottomTabBarStyle({
            normal: new SymbolGlyphModifier(icon)
        }, title)
        .padding({ bottom: 4 });
    }

    build() {
        Tabs({ controller: this.tabController, index: this.currentIndex }) {
            this.TabContentsBuilder()
        }
        .width('100%')
        .height('100%')
        .backgroundColor('#0A0A1A')
        .barPosition(BarPosition.End)
        .scrollable(false)
        .animationMode(AnimationMode.NO_ANIMATION)
        .onChange((index: number) => {
            this.currentIndex = index;
        })
    }
}