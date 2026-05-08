if (!("finalizeConstruction" in ViewPU.prototype)) {
    Reflect.set(ViewPU.prototype, "finalizeConstruction", () => { });
}
interface ImmersiveTabNavigation_Params {
    currentIndex?: number;
    contentBuilder?: () => void;
    onTabChange?: (index: number) => void;
    windowFocused?: boolean;
    bottomAvoidHeight?: number;
}
import { defaultLogger } from "@normalized:N&&&@ohos/common/src/main/ets/util/Logger&1.0.0";
import window from "@ohos:window";
import type { BusinessError } from "@ohos:base";
const THEME_COLOR = '#7C4DFF';
export class ImmersiveTabNavigation extends ViewPU {
    constructor(parent, params, __localStorage, elmtId = -1, paramsLambda = undefined, extraInfo) {
        super(parent, __localStorage, elmtId, extraInfo);
        if (typeof paramsLambda === "function") {
            this.paramsGenerator_ = paramsLambda;
        }
        this.__currentIndex = new ObservedPropertySimplePU(0, this, "currentIndex");
        this.contentBuilder = undefined;
        this.onTabChange = undefined;
        this.windowFocused = true;
        this.bottomAvoidHeight = 0;
        this.setInitiallyProvidedValue(params);
        this.finalizeConstruction();
    }
    setInitiallyProvidedValue(params: ImmersiveTabNavigation_Params) {
        if (params.currentIndex !== undefined) {
            this.currentIndex = params.currentIndex;
        }
        if (params.contentBuilder !== undefined) {
            this.contentBuilder = params.contentBuilder;
        }
        if (params.onTabChange !== undefined) {
            this.onTabChange = params.onTabChange;
        }
        if (params.windowFocused !== undefined) {
            this.windowFocused = params.windowFocused;
        }
        if (params.bottomAvoidHeight !== undefined) {
            this.bottomAvoidHeight = params.bottomAvoidHeight;
        }
    }
    updateStateVars(params: ImmersiveTabNavigation_Params) {
    }
    purgeVariableDependenciesOnElmtId(rmElmtId) {
        this.__currentIndex.purgeDependencyOnElmtId(rmElmtId);
    }
    aboutToBeDeleted() {
        this.__currentIndex.aboutToBeDeleted();
        SubscriberManager.Get().delete(this.id__());
        this.aboutToBeDeletedInternal();
    }
    private __currentIndex: ObservedPropertySimplePU<number>;
    get currentIndex() {
        return this.__currentIndex.get();
    }
    set currentIndex(newValue: number) {
        this.__currentIndex.set(newValue);
    }
    private __contentBuilder;
    private onTabChange?: (index: number) => void;
    private windowFocused: boolean;
    private bottomAvoidHeight: number;
    aboutToAppear() {
        const mainWindow = AppStorage.get<window.Window>('main_window');
        if (mainWindow) {
            try {
                const avoidArea = mainWindow.getWindowAvoidArea(window.AvoidAreaType.TYPE_SYSTEM);
                this.bottomAvoidHeight = avoidArea.bottomRect.height || 0;
            }
            catch (e) {
                defaultLogger.error('Failed to get avoid area: ' + (e as BusinessError).message);
            }
        }
    }
    triggerTabSwitchFeedback(index: number) {
        this.currentIndex = index;
        AppStorage.setOrCreate('global_theme_color', THEME_COLOR);
        this.onTabChange?.(index);
    }
    tabBarBuilder(index: number, icon: string, label: string, parent = null) {
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Column.create();
            Column.width('100%');
            Column.height(56);
            Column.justifyContent(FlexAlign.Center);
            Column.alignItems(HorizontalAlign.Center);
        }, Column);
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            If.create();
            if (this.currentIndex === index && this.windowFocused) {
                this.ifElseBranchUpdateFunction(0, () => {
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        Circle.create();
                        Circle.width(32);
                        Circle.height(32);
                        Circle.backgroundColor(`${THEME_COLOR}33`);
                        Circle.blur(8);
                        Circle.position({ x: '50%', y: '50%' });
                        Circle.translate({ x: '-50%', y: '-50%' });
                    }, Circle);
                });
            }
            else {
                this.ifElseBranchUpdateFunction(1, () => {
                });
            }
        }, If);
        If.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Text.create(icon);
            Text.fontSize(20);
            Text.opacity(this.currentIndex === index ? 1 : 0.5);
        }, Text);
        Text.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Text.create(label);
            Text.fontSize(10);
            Text.fontColor(this.currentIndex === index ? THEME_COLOR : '#999');
            Text.fontWeight(this.currentIndex === index ? FontWeight.Bold : FontWeight.Normal);
        }, Text);
        Text.pop();
        Column.pop();
    }
    initialRender() {
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Stack.create();
            Stack.width('100%');
            Stack.height('100%');
            Stack.backgroundColor('#00000000');
        }, Stack);
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Column.create();
            Column.width('100%');
            Column.height('100%');
        }, Column);
        this.contentBuilder.bind(this)();
        Column.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Column.create();
            Column.width('92%');
            Column.height(72);
            Column.alignSelf(ItemAlign.Center);
            Column.position({ y: `calc(100% - ${this.bottomAvoidHeight > 0 ? this.bottomAvoidHeight : 16}px - 72px)` });
            Column.borderRadius(24);
            Column.shadow({
                radius: 20,
                offsetY: -4,
                color: 'rgba(0,0,0,0.15)'
            });
        }, Column);
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Stack.create();
            Stack.width('100%');
            Stack.height('100%');
        }, Stack);
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Column.create();
            Column.width('100%');
            Column.height('100%');
            Column.backgroundBlurStyle(BlurStyle.Regular);
            Column.borderRadius(24);
        }, Column);
        Column.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Column.create();
            Column.width('100%');
            Column.height('100%');
            Column.backgroundColor(`${THEME_COLOR}0D`);
            Column.borderRadius(24);
        }, Column);
        Column.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Column.create();
            Column.width('100%');
            Column.height('100%');
            Column.linearGradient({
                angle: 180,
                colors: [['rgba(255,255,255,0.15)', 0.0], ['rgba(255,255,255,0.05)', 1.0]]
            });
            Column.borderRadius(24);
        }, Column);
        Column.pop();
        Stack.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Tabs.create({ index: this.currentIndex });
            Tabs.width('100%');
            Tabs.height(64);
            Tabs.barPosition(BarPosition.End);
            Tabs.onChange((index: number) => {
                this.triggerTabSwitchFeedback(index);
            });
        }, Tabs);
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            TabContent.create(() => {
                this.observeComponentCreation2((elmtId, isInitialRender) => {
                    Column.create();
                }, Column);
                this.observeComponentCreation2((elmtId, isInitialRender) => {
                    Blank.create();
                }, Blank);
                Blank.pop();
                Column.pop();
            });
            TabContent.tabBar({ builder: () => {
                    this.tabBarBuilder.call(this, 0, '🌌', 'TrulyMEM');
                } });
        }, TabContent);
        TabContent.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            TabContent.create(() => {
                this.observeComponentCreation2((elmtId, isInitialRender) => {
                    Column.create();
                }, Column);
                this.observeComponentCreation2((elmtId, isInitialRender) => {
                    Blank.create();
                }, Blank);
                Blank.pop();
                Column.pop();
            });
            TabContent.tabBar({ builder: () => {
                    this.tabBarBuilder.call(this, 1, '⚙', '设置');
                } });
        }, TabContent);
        TabContent.pop();
        Tabs.pop();
        Column.pop();
        Stack.pop();
    }
    rerender() {
        this.updateDirtyElements();
    }
}
