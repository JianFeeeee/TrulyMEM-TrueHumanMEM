if (!("finalizeConstruction" in ViewPU.prototype)) {
    Reflect.set(ViewPU.prototype, "finalizeConstruction", () => { });
}
interface SettingsPage_Params {
    baseUrl?: string;
    model?: string;
    apiKey?: string;
    pref?: dataPreferences.Preferences;
}
import dataPreferences from "@ohos:data.preferences";
export class SettingsPage extends ViewPU {
    constructor(parent, params, __localStorage, elmtId = -1, paramsLambda = undefined, extraInfo) {
        super(parent, __localStorage, elmtId, extraInfo);
        if (typeof paramsLambda === "function") {
            this.paramsGenerator_ = paramsLambda;
        }
        this.__baseUrl = new ObservedPropertySimplePU('', this, "baseUrl");
        this.__model = new ObservedPropertySimplePU('', this, "model");
        this.__apiKey = new ObservedPropertySimplePU('', this, "apiKey");
        this.pref = undefined;
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
        if (params.pref !== undefined) {
            this.pref = params.pref;
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
    private pref?: dataPreferences.Preferences;
    async aboutToAppear() {
        const ctx = getContext(this);
        this.pref = await dataPreferences.getPreferences(ctx, 'trulymem_config');
        this.baseUrl = String(await this.pref.get('base_url', 'https://api.deepseek.com'));
        this.model = String(await this.pref.get('model', 'deepseek-chat'));
        this.apiKey = String(await this.pref.get('api_key', ''));
    }
    async onBaseUrlChange(value: string) {
        this.baseUrl = value;
        await this.pref?.put('base_url', value);
        await this.pref?.flush();
    }
    async onModelChange(value: string) {
        this.model = value;
        await this.pref?.put('model', value);
        await this.pref?.flush();
    }
    async onApiKeyChange(value: string) {
        this.apiKey = value;
        await this.pref?.put('api_key', value);
        await this.pref?.flush();
    }
    initialRender() {
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Column.create();
            Column.width('100%');
            Column.height('100%');
            Column.padding(16);
        }, Column);
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Text.create('API 配置');
            Text.fontSize(24);
            Text.fontWeight(FontWeight.Bold);
            Text.margin({ top: 20, bottom: 16 });
        }, Text);
        Text.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Text.create('Base URL');
            Text.fontSize(14);
            Text.width('100%');
            Text.margin({ left: 16 });
        }, Text);
        Text.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            TextInput.create({ placeholder: 'https://api.deepseek.com', text: this.baseUrl });
            TextInput.onChange((v: string) => { this.onBaseUrlChange(v); });
            TextInput.margin({ left: 16, right: 16, bottom: 12 });
        }, TextInput);
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Text.create('Model ID');
            Text.fontSize(14);
            Text.width('100%');
            Text.margin({ left: 16 });
        }, Text);
        Text.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            TextInput.create({ placeholder: 'deepseek-chat', text: this.model });
            TextInput.onChange((v: string) => { this.onModelChange(v); });
            TextInput.margin({ left: 16, right: 16, bottom: 12 });
        }, TextInput);
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Text.create('API Key');
            Text.fontSize(14);
            Text.width('100%');
            Text.margin({ left: 16 });
        }, Text);
        Text.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            TextInput.create({ placeholder: 'sk-...', text: this.apiKey });
            TextInput.type(InputType.Password);
            TextInput.onChange((v: string) => { this.onApiKeyChange(v); });
            TextInput.margin({ left: 16, right: 16, bottom: 12 });
        }, TextInput);
        Column.pop();
    }
    rerender() {
        this.updateDirtyElements();
    }
}
