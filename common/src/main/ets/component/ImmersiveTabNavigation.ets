import { defaultLogger } from '../util/Logger';
import { window } from '@kit.ArkUI';
import { BusinessError } from '@kit.BasicServicesKit';

const THEME_COLOR = '#7C4DFF';

@Component
export struct ImmersiveTabNavigation {
  @State currentIndex: number = 0;
  @BuilderParam contentBuilder: () => void;
  onTabChange?: (index: number) => void;

  private windowFocused: boolean = true;
  private bottomAvoidHeight: number = 0;

  aboutToAppear() {
    const mainWindow = AppStorage.get<window.Window>('main_window');
    if (mainWindow) {
      try {
        const avoidArea = mainWindow.getWindowAvoidArea(window.AvoidAreaType.TYPE_SYSTEM);
        this.bottomAvoidHeight = avoidArea.bottomRect.height || 0;
      } catch (e) {
        defaultLogger.error('Failed to get avoid area: ' + (e as BusinessError).message);
      }
    }
  }

  triggerTabSwitchFeedback(index: number) {
    this.currentIndex = index;
    AppStorage.setOrCreate('global_theme_color', THEME_COLOR);
    this.onTabChange?.(index);
  }

  @Builder
  tabBarBuilder(index: number, icon: string, label: string) {
    Column() {
      if (this.currentIndex === index && this.windowFocused) {
        Circle()
          .width(32)
          .height(32)
          .backgroundColor(`${THEME_COLOR}33`)
          .blur(8)
          .position({ x: '50%', y: '50%' })
          .translate({ x: '-50%', y: '-50%' })
      }

      Text(icon)
        .fontSize(20)
        .opacity(this.currentIndex === index ? 1 : 0.5)

      Text(label)
        .fontSize(10)
        .fontColor(this.currentIndex === index ? THEME_COLOR : '#999')
        .fontWeight(this.currentIndex === index ? FontWeight.Bold : FontWeight.Normal)
    }
    .width('100%')
    .height(56)
    .justifyContent(FlexAlign.Center)
    .alignItems(HorizontalAlign.Center)
  }

  build() {
    Stack() {
      Column() {
        this.contentBuilder()
      }
      .width('100%')
      .height('100%')

      Column() {
        Stack() {
          Column()
            .width('100%')
            .height('100%')
            .backgroundBlurStyle(BlurStyle.Regular)
            .borderRadius(24)

          Column()
            .width('100%')
            .height('100%')
            .backgroundColor(`${THEME_COLOR}0D`)
            .borderRadius(24)

          Column()
            .width('100%')
            .height('100%')
            .linearGradient({
              angle: 180,
              colors: [['rgba(255,255,255,0.15)', 0.0], ['rgba(255,255,255,0.05)', 1.0]]
            })
            .borderRadius(24)
        }
        .width('100%')
        .height('100%')

        Tabs({ index: this.currentIndex }) {
          TabContent() {
            Column() {
              Blank()
            }
          }
          .tabBar(this.tabBarBuilder(0, '🌌', 'TrulyMEM'))

          TabContent() {
            Column() {
              Blank()
            }
          }
          .tabBar(this.tabBarBuilder(1, '⚙', '设置'))
        }
        .width('100%')
        .height(64)
        .barPosition(BarPosition.End)
        .onChange((index: number) => {
          this.triggerTabSwitchFeedback(index);
        })
      }
      .width('92%')
      .height(72)
      .alignSelf(ItemAlign.Center)
      .position({ y: `calc(100% - ${this.bottomAvoidHeight > 0 ? this.bottomAvoidHeight : 16}px - 72px)` })
      .borderRadius(24)
      .shadow({
        radius: 20,
        offsetY: -4,
        color: 'rgba(0,0,0,0.15)'
      })
    }
    .width('100%')
    .height('100%')
    .backgroundColor('#00000000')
  }
}
