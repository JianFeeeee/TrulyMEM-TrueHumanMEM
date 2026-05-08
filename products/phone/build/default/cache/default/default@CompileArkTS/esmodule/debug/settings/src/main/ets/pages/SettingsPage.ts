if (!("finalizeConstruction" in ViewPU.prototype)) {
    Reflect.set(ViewPU.prototype, "finalizeConstruction", () => { });
}
interface SettingsPage_Params {
    baseUrl?: string;
    model?: string;
    apiKey?: string;
    store?: AppConfigStore;
}
import { SettingsSectionHeader, SettingInputItem, GlowBackground, AppConfigStore } from "@normalized:N&&&@ohos/settings/src/main/ets/components/SettingsComponents&1.0.0";
export class SettingsPage extends ViewPU {
    constructor(parent, params, __localStorage, elmtId = -1, paramsLambda = undefined, extraInfo) {
        super(parent, __localStorage, elmtId, extraInfo);
        if (typeof paramsLambda === "function") {
            this.paramsGenerator_ = paramsLambda;
        }
        this.__baseUrl = new ObservedPropertySimplePU('', this, "baseUrl");
        this.__model = new ObservedPropertySimplePU('', this, "model");
        this.__apiKey = new ObservedPropertySimplePU('', this, "apiKey");
        this.store = new AppConfigStore();
        this.setInitiallyProvidedValue(params);
        this.finalizeConstruction();
    }
    setInitiallyProvidedValue(params: SettingsPage_Params) {
        if (params.baseUrl !== undefined) {
            this.baseUrl = params.baseUrl;
        }
        if (params.model !== undefined) {
            this.model = params.model;
        }
        if (params.apiKey !== undefined) {
            this.apiKey = params.apiKey;
        }
        if (params.store !== undefined) {
            this.store = params.store;
        }
    }
    updateStateVars(params: SettingsPage_Params) {
    }
    purgeVariableDependenciesOnElmtId(rmElmtId) {
        this.__baseUrl.purgeDependencyOnElmtId(rmElmtId);
        this.__model.purgeDependencyOnElmtId(rmElmtId);
        this.__apiKey.purgeDependencyOnElmtId(rmElmtId);
    }
    aboutToBeDeleted() {
        this.__baseUrl.aboutToBeDeleted();
        this.__model.aboutToBeDeleted();
        this.__apiKey.aboutToBeDeleted();
        SubscriberManager.Get().delete(this.id__());
        this.aboutToBeDeletedInternal();
    }
    private __baseUrl: ObservedPropertySimplePU<string>;
    get baseUrl() {
        return this.__baseUrl.get();
    }
    set baseUrl(newValue: string) {
        this.__baseUrl.set(newValue);
    }
    private __model: ObservedPropertySimplePU<string>;
    get model() {
        return this.__model.get();
    }
    set model(newValue: string) {
        this.__model.set(newValue);
    }
    private __apiKey: ObservedPropertySimplePU<string>;
    get apiKey() {
        return this.__apiKey.get();
    }
    set apiKey(newValue: string) {
        this.__apiKey.set(newValue);
    }
    private store: AppConfigStore;
    async aboutToAppear() {
        const ctx = getContext(this);
        await this.store.init(ctx);
        this.baseUrl = await this.store.getString('base_url', 'https://api.deepseek.com');
        this.model = await this.store.getString('model', 'deepseek-chat');
        this.apiKey = await this.store.getString('api_key', '');
    }
    private async saveConfig(key: string, value: string): Promise<void> {
        await this.store.setString(key, value);
    }
    initialRender() {
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Stack.create();
            Stack.width('100%');
            Stack.height('100%');
            Stack.backgroundColor('rgba(26,27,46,0.95)');
            Stack.backgroundBlurStyle(BlurStyle.Regular);
        }, Stack);
        {
            this.observeComponentCreation2((elmtId, isInitialRender) => {
                if (isInitialRender) {
                    let componentCall = new GlowBackground(this, {}, undefined, elmtId, () => { }, { page: "features/settings/src/main/ets/pages/SettingsPage.ets", line: 25, col: 13 });
                    ViewPU.create(componentCall);
                    let paramsLambda = () => {
                        return {};
                    };
                    componentCall.paramsGenerator_ = paramsLambda;
                }
                else {
                    this.updateStateVarsOfChildByElmtId(elmtId, {});
                }
            }, { name: "GlowBackground" });
        }
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Column.create();
            Column.padding(16);
            Column.width('100%');
        }, Column);
        {
            this.observeComponentCreation2((elmtId, isInitialRender) => {
                if (isInitialRender) {
                    let componentCall = new SettingsSectionHeader(this, { title: 'API 配置' }, undefined, elmtId, () => { }, { page: "features/settings/src/main/ets/pages/SettingsPage.ets", line: 28, col: 17 });
                    ViewPU.create(componentCall);
                    let paramsLambda = () => {
                        return {
                            title: 'API 配置'
                        };
                    };
                    componentCall.paramsGenerator_ = paramsLambda;
                }
                else {
                    this.updateStateVarsOfChildByElmtId(elmtId, {
                        title: 'API 配置'
                    });
                }
            }, { name: "SettingsSectionHeader" });
        }
        {
            this.observeComponentCreation2((elmtId, isInitialRender) => {
                if (isInitialRender) {
                    let componentCall = new SettingInputItem(this, {
                        label: 'Base URL',
                        placeholder: 'https://api.deepseek.com',
                        value: this.__baseUrl,
                        onValueChange: (v: string): void => { this.saveConfig('base_url', v); }
                    }, undefined, elmtId, () => { }, { page: "features/settings/src/main/ets/pages/SettingsPage.ets", line: 30, col: 17 });
                    ViewPU.create(componentCall);
                    let paramsLambda = () => {
                        return {
                            label: 'Base URL',
                            placeholder: 'https://api.deepseek.com',
                            value: this.baseUrl,
                            onValueChange: (v: string): void => { this.saveConfig('base_url', v); }
                        };
                    };
                    componentCall.paramsGenerator_ = paramsLambda;
                }
                else {
                    this.updateStateVarsOfChildByElmtId(elmtId, {
                        label: 'Base URL',
                        placeholder: 'https://api.deepseek.com'
                    });
                }
            }, { name: "SettingInputItem" });
        }
        {
            this.observeComponentCreation2((elmtId, isInitialRender) => {
                if (isInitialRender) {
                    let componentCall = new SettingInputItem(this, {
                        label: 'Model ID',
                        placeholder: 'deepseek-chat',
                        value: this.__model,
                        onValueChange: (v: string): void => { this.saveConfig('model', v); }
                    }, undefined, elmtId, () => { }, { page: "features/settings/src/main/ets/pages/SettingsPage.ets", line: 37, col: 17 });
                    ViewPU.create(componentCall);
                    let paramsLambda = () => {
                        return {
                            label: 'Model ID',
                            placeholder: 'deepseek-chat',
                            value: this.model,
                            onValueChange: (v: string): void => { this.saveConfig('model', v); }
                        };
                    };
                    componentCall.paramsGenerator_ = paramsLambda;
                }
                else {
                    this.updateStateVarsOfChildByElmtId(elmtId, {
                        label: 'Model ID',
                        placeholder: 'deepseek-chat'
                    });
                }
            }, { name: "SettingInputItem" });
        }
        {
            this.observeComponentCreation2((elmtId, isInitialRender) => {
                if (isInitialRender) {
                    let componentCall = new SettingInputItem(this, {
                        label: 'API Key',
                        placeholder: 'sk-...',
                        value: this.__apiKey,
                        isPassword: true,
                        onValueChange: (v: string): void => { this.saveConfig('api_key', v); }
                    }, undefined, elmtId, () => { }, { page: "features/settings/src/main/ets/pages/SettingsPage.ets", line: 44, col: 17 });
                    ViewPU.create(componentCall);
                    let paramsLambda = () => {
                        return {
                            label: 'API Key',
                            placeholder: 'sk-...',
                            value: this.apiKey,
                            isPassword: true,
                            onValueChange: (v: string): void => { this.saveConfig('api_key', v); }
                        };
                    };
                    componentCall.paramsGenerator_ = paramsLambda;
                }
                else {
                    this.updateStateVarsOfChildByElmtId(elmtId, {
                        label: 'API Key',
                        placeholder: 'sk-...'
                    });
                }
            }, { name: "SettingInputItem" });
        }
        Column.pop();
        Stack.pop();
    }
    rerender() {
        this.updateDirtyElements();
    }
}
