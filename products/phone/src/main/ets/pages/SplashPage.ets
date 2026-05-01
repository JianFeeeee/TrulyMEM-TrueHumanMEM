import { PromptAction } from '@kit.ArkUI';

@Entry
@Component
struct SplashPage {
  aboutToAppear() {
    setTimeout(() => {
      const uiContext = this.getUIContext();
      if (uiContext) {
        const router = uiContext.getRouter();
        router.replaceUrl({ url: 'pages/Index' });
      }
    }, 2000);
  }

  build() {
    Column() {
      Text('TrulyMEM')
        .fontSize(48)
        .fontWeight(FontWeight.Bold)
        .fontColor(Color.White);
      Text('True Human Memory')
        .fontSize(20)
        .fontColor(Color.White)
        .margin({ top: 16 });
    }
    .width('100%')
    .height('100%')
    .backgroundColor('#1A1B2E')
    .justifyContent(FlexAlign.Center)
    .alignItems(HorizontalAlign.Center);
  }
}
