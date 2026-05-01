import { GraphDatabase, Logger, ImmersiveTabNavigation } from '@ohos/common';
import { GraphPage } from '@ohos/graph';
import { ChatPage } from '@ohos/chat';
import { SettingsPage } from '@ohos/settings';
import display from '@ohos.display';

@Builder
export function MainPageBuilder() {
  MainPage({ db: new GraphDatabase() })
}

@Component
export struct MainPage {
    @Prop db: GraphDatabase;
    @State isWide: boolean = false;
    @State currentIndex: number = 0;

    aboutToAppear() {
        this.updateBreakpoint();
        try {
            display.on('change', () => { this.updateBreakpoint(); });
        } catch (e) {
            Logger.error('display.on error: ' + JSON.stringify(e));
        }
    }

    private updateBreakpoint(): void {
        try {
            const defaultWindow = display.getDefaultDisplaySync();
            this.isWide = defaultWindow.width > 520;
        } catch (e) {
            Logger.error('updateBreakpoint error: ' + JSON.stringify(e));
        }
    }

  @Builder
  TrulyMEMContent() {
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

  @Builder
  SettingsContent() {
    SettingsPage()
  }

  @Builder
  TabContentBuilder() {
    if (this.currentIndex === 0) {
      this.TrulyMEMContent()
    } else {
      this.SettingsContent()
    }
  }

  build() {
    ImmersiveTabNavigation({
      contentBuilder: this.TabContentBuilder,
      onTabChange: (index: number) => {
        this.currentIndex = index;
      }
    })
    .width('100%')
    .height('100%')
  }
}