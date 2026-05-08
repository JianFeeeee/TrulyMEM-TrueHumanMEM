if (!("finalizeConstruction" in ViewPU.prototype)) {
    Reflect.set(ViewPU.prototype, "finalizeConstruction", () => { });
}
interface GlowBackground_Params {
    color?: string;
    glowSize?: number;
}
interface SettingInputItem_Params {
    label?: string;
    placeholder?: string;
    value?: string;
    isPassword?: boolean;
    onValueChange?: (value: string) => void;
}
interface SettingsSectionHeader_Params {
    title?: string;
}
import dataPreferences from "@ohos:data.preferences";
import type common from "@ohos:app.ability.common";
export class SettingsSectionHeader extends ViewPU {
    constructor(parent, params, __localStorage, elmtId = -1, paramsLambda = undefined, extraInfo) {
        super(parent, __localStorage, elmtId, extraInfo);
        if (typeof paramsLambda === "function") {
            this.paramsGenerator_ = paramsLambda;
        }
        this.__title = new SynchedPropertySimpleOneWayPU(params.title, this, "title");
        this.setInitiallyProvidedValue(params);
        this.finalizeConstruction();
    }
    setInitiallyProvidedValue(params: SettingsSectionHeader_Params) {
    }
    updateStateVars(params: SettingsSectionHeader_Params) {
        this.__title.reset(params.title);
    }
    purgeVariableDependenciesOnElmtId(rmElmtId) {
        this.__title.purgeDependencyOnElmtId(rmElmtId);
    }
    aboutToBeDeleted() {
        this.__title.aboutToBeDeleted();
        SubscriberManager.Get().delete(this.id__());
        this.aboutToBeDeletedInternal();
    }
    private __title: SynchedPropertySimpleOneWayPU<string>;
    get title() {
        return this.__title.get();
    }
    set title(newValue: string) {
        this.__title.set(newValue);
    }
    initialRender() {
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Text.create(this.title);
            Text.fontSize(24);
            Text.fontWeight(FontWeight.Bold);
            Text.fontColor('#FFFFFF');
            Text.margin({ top: 20, bottom: 16 });
        }, Text);
        Text.pop();
    }
    rerender() {
        this.updateDirtyElements();
    }
}
export class SettingInputItem extends ViewPU {
    constructor(parent, params, __localStorage, elmtId = -1, paramsLambda = undefined, extraInfo) {
        super(parent, __localStorage, elmtId, extraInfo);
        if (typeof paramsLambda === "function") {
            this.paramsGenerator_ = paramsLambda;
        }
        this.__label = new SynchedPropertySimpleOneWayPU(params.label, this, "label");
        this.__placeholder = new SynchedPropertySimpleOneWayPU(params.placeholder, this, "placeholder");
        this.__value = new SynchedPropertySimpleTwoWayPU(params.value, this, "value");
        this.isPassword = false;
        this.onValueChange = undefined;
        this.setInitiallyProvidedValue(params);
        this.finalizeConstruction();
    }
    setInitiallyProvidedValue(params: SettingInputItem_Params) {
        if (params.isPassword !== undefined) {
            this.isPassword = params.isPassword;
        }
        if (params.onValueChange !== undefined) {
            this.onValueChange = params.onValueChange;
        }
    }
    updateStateVars(params: SettingInputItem_Params) {
        this.__label.reset(params.label);
        this.__placeholder.reset(params.placeholder);
    }
    purgeVariableDependenciesOnElmtId(rmElmtId) {
        this.__label.purgeDependencyOnElmtId(rmElmtId);
        this.__placeholder.purgeDependencyOnElmtId(rmElmtId);
        this.__value.purgeDependencyOnElmtId(rmElmtId);
    }
    aboutToBeDeleted() {
        this.__label.aboutToBeDeleted();
        this.__placeholder.aboutToBeDeleted();
        this.__value.aboutToBeDeleted();
        SubscriberManager.Get().delete(this.id__());
        this.aboutToBeDeletedInternal();
    }
    private __label: SynchedPropertySimpleOneWayPU<string>;
    get label() {
        return this.__label.get();
    }
    set label(newValue: string) {
        this.__label.set(newValue);
    }
    private __placeholder: SynchedPropertySimpleOneWayPU<string>;
    get placeholder() {
        return this.__placeholder.get();
    }
    set placeholder(newValue: string) {
        this.__placeholder.set(newValue);
    }
    private __value: SynchedPropertySimpleTwoWayPU<string>;
    get value() {
        return this.__value.get();
    }
    set value(newValue: string) {
        this.__value.set(newValue);
    }
    private isPassword?: boolean;
    private onValueChange?: (value: string) => void;
    initialRender() {
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Column.create();
            Column.padding(12);
            Column.backgroundColor('rgba(255,255,255,0.05)');
            Column.borderRadius(12);
            Column.backgroundBlurStyle(BlurStyle.Thin);
            Column.margin({ bottom: 12 });
        }, Column);
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Text.create(this.label);
            Text.fontSize(14);
            Text.fontColor('#FFFFFF');
            Text.width('100%');
            Text.margin({ bottom: 8 });
        }, Text);
        Text.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            TextInput.create({ placeholder: this.placeholder, text: this.value });
            TextInput.type(this.isPassword ? InputType.Password : InputType.Normal);
            TextInput.onChange((v: string) => {
                this.value = v;
                this.onValueChange?.(v);
            });
            TextInput.backgroundColor('rgba(255,255,255,0.1)');
            TextInput.borderRadius(8);
            TextInput.border({ width: 1, color: 'rgba(124,77,255,0.3)' });
            TextInput.height(40);
        }, TextInput);
        Column.pop();
    }
    rerender() {
        this.updateDirtyElements();
    }
}
export class GlowBackground extends ViewPU {
    constructor(parent, params, __localStorage, elmtId = -1, paramsLambda = undefined, extraInfo) {
        super(parent, __localStorage, elmtId, extraInfo);
        if (typeof paramsLambda === "function") {
            this.paramsGenerator_ = paramsLambda;
        }
        this.__color = new SynchedPropertySimpleOneWayPU(params.color, this, "color");
        this.__glowSize = new SynchedPropertySimpleOneWayPU(params.glowSize, this, "glowSize");
        this.setInitiallyProvidedValue(params);
        this.finalizeConstruction();
    }
    setInitiallyProvidedValue(params: GlowBackground_Params) {
        if (params.color === undefined) {
            this.__color.set('rgba(124,77,255,0.15)');
        }
        if (params.glowSize === undefined) {
            this.__glowSize.set(200);
        }
    }
    updateStateVars(params: GlowBackground_Params) {
        this.__color.reset(params.color);
        this.__glowSize.reset(params.glowSize);
    }
    purgeVariableDependenciesOnElmtId(rmElmtId) {
        this.__color.purgeDependencyOnElmtId(rmElmtId);
        this.__glowSize.purgeDependencyOnElmtId(rmElmtId);
    }
    aboutToBeDeleted() {
        this.__color.aboutToBeDeleted();
        this.__glowSize.aboutToBeDeleted();
        SubscriberManager.Get().delete(this.id__());
        this.aboutToBeDeletedInternal();
    }
    private __color: SynchedPropertySimpleOneWayPU<string>;
    get color() {
        return this.__color.get();
    }
    set color(newValue: string) {
        this.__color.set(newValue);
    }
    private __glowSize: SynchedPropertySimpleOneWayPU<number>;
    get glowSize() {
        return this.__glowSize.get();
    }
    set glowSize(newValue: number) {
        this.__glowSize.set(newValue);
    }
    initialRender() {
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Column.create();
            Column.width(this.glowSize);
            Column.height(this.glowSize);
            Column.backgroundColor(this.color);
            Column.blur(40);
            Column.borderRadius(this.glowSize / 2);
            Column.position({ x: '10%', y: '20%' });
        }, Column);
        Column.pop();
    }
    rerender() {
        this.updateDirtyElements();
    }
}
/**
 * AppConfigStore — 应用配置存储封装
 * 封装 Preferences 读写，提供类型安全访问
 */
export class AppConfigStore {
    private pref?: dataPreferences.Preferences;
    private readonly storeName: string = 'trulymem_config';
    async init(ctx: common.Context): Promise<void> {
        this.pref = await dataPreferences.getPreferences(ctx, this.storeName);
    }
    async getString(key: string, defaultValue: string): Promise<string> {
        return String(await this.pref?.get(key, defaultValue));
    }
    async setString(key: string, value: string): Promise<void> {
        await this.pref?.put(key, value);
        await this.pref?.flush();
    }
    static async create(ctx: common.Context): Promise<AppConfigStore> {
        const store = new AppConfigStore();
        await store.init(ctx);
        return store;
    }
}
