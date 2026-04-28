import AbilityConstant from '@ohos.app.ability.AbilityConstant';
import UIAbility from '@ohos.app.ability.UIAbility';
import Window from '@ohos.app.ability.Window';
import Want from '@ohos.app.ability.Want';

export default class EntryAbility extends UIAbility {
    onCreate(want: Want, param: AbilityConstant.LaunchParam): void {
        console.info('EntryAbility onCreate');
    }

    onDestroy(): void {
        console.info('EntryAbility onDestroy');
    }

    onWindowStageCreate(windowStage: Window.WindowStage): void {
        windowStage.loadContent('pages/Index', (err, data) => {
            if (err.code) {
                console.error('Failed to load content: ' + JSON.stringify(err));
                return;
            }
            console.info('Succeeded in loading content: ' + JSON.stringify(data));
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
