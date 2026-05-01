import { UIAbility, AbilityConstant, Want } from '@kit.AbilityKit';
import { window } from '@kit.ArkUI';
import { BusinessError } from '@kit.BasicServicesKit';
import { defaultLogger } from '@ohos/common';

export default class EntryAbility extends UIAbility {
  onCreate(want: Want, param: AbilityConstant.LaunchParam): void {
    defaultLogger.info('EntryAbility onCreate');
  }

  onDestroy(): void {
    defaultLogger.info('EntryAbility onDestroy');
  }

  onWindowStageCreate(windowStage: window.WindowStage): void {
    const windowClass: window.Window = windowStage.getMainWindowSync();
    try {
      windowClass.setWindowBackgroundColor('#00000000');
    } catch (e) {
      defaultLogger.error('Failed to set background color: ' + (e as BusinessError).message);
    }
    try {
      windowClass.setWindowSystemBarProperties({
        statusBarColor: '#00000000',
        navigationBarColor: '#00000000'
      });
    } catch (e) {
      defaultLogger.error('Failed to set system bar properties: ' + (e as BusinessError).message);
    }

    defaultLogger.info('EntryAbility onWindowStageCreate');
    windowStage.loadContent('pages/SplashPage', (err, data) => {
      if (err.code) {
        defaultLogger.error('Failed to load the content. Cause: ' + JSON.stringify(err));
        return;
      }
      defaultLogger.info('Succeeded in loading the content. Data: ' + JSON.stringify(data));
    });
  }

  onWindowStageDestroy(): void {
    defaultLogger.info('EntryAbility onWindowStageDestroy');
  }

  onForeground(): void {
    defaultLogger.info('EntryAbility onForeground');
  }

  onBackground(): void {
    defaultLogger.info('EntryAbility onBackground');
  }
}