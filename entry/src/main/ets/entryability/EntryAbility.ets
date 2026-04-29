import { UIAbility, AbilityConstant, Want } from '@kit.AbilityKit';
import { window } from '@kit.ArkUI';
import { BusinessError } from '@kit.BasicServicesKit';

export default class EntryAbility extends UIAbility {
    onCreate(want: Want, param: AbilityConstant.LaunchParam): void {
        console.info('EntryAbility onCreate');
    }

    onDestroy(): void {
        console.info('EntryAbility onDestroy');
    }

    onWindowStageCreate(windowStage: window.WindowStage): void {
        const windowClass: window.Window = windowStage.getMainWindowSync();

        try {
            windowClass.setWindowBackgroundColor('#00000000');
        } catch (e) {
            console.error('Failed to set background color: ' + (e as BusinessError).message);
        }

        try {
            windowClass.setWindowSystemBarProperties({
                statusBarColor: '#00000000',
                navigationBarColor: '#00000000',
                statusBarContentColor: '#FFFFFF',
                navigationBarContentColor: '#FFFFFF'
            });
        } catch (e) {
            console.error('Failed to set system bar: ' + (e as BusinessError).message);
        }

        AppStorage.setOrCreate('main_window', windowClass);

        windowStage.loadContent('pages/Index', (err: BusinessError) => {
            if (err.code) {
                console.error('Failed to load content: ' + err.message);
                return;
            }
            console.info('Succeeded in loading content');
        });
    }

    onWindowStageDestroy(): void {
        console.info('EntryAbility onWindowStageDestroy');
    }

    onForeground(): void {
        console.info('EntryAbility onForeground');
    }

    onBackground(): void {
        console.info('EntryAbility onBackground');
    }
}
