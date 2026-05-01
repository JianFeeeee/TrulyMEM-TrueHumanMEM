import dataPreferences from '@ohos.data.preferences';

/**
 * SettingsSectionHeader — 设置区块标题
 * 大标题 + 加粗白色
 */
@Component
export struct SettingsSectionHeader {
  @Prop title: string;

  build() {
    Text(this.title)
      .fontSize(24)
      .fontWeight(FontWeight.Bold)
      .fontColor('#FFFFFF')
      .margin({ top: 20, bottom: 16 })
  }
}

/**
 * SettingInputItem — 设置输入项
 * 标签 + TextInput，统一玻璃拟态风格
 */
@Component
export struct SettingInputItem {
  @Prop label: string;
  @Prop placeholder: string;
  @Link value: string;
  isPassword?: boolean = false;
  onValueChange?: (value: string) => void;

  build() {
    Column() {
      Text(this.label)
        .fontSize(14)
        .fontColor('#FFFFFF')
        .width('100%')
        .margin({ bottom: 8 })

      TextInput({ placeholder: this.placeholder, text: this.value })
        .type(this.isPassword ? InputType.Password : InputType.Normal)
        .onChange((v: string) => {
          this.value = v;
          this.onValueChange?.(v);
        })
        .backgroundColor('rgba(255,255,255,0.1)')
        .borderRadius(8)
        .border({ width: 1, color: 'rgba(124,77,255,0.3)' })
        .height(40)
    }
    .padding(12)
    .backgroundColor('rgba(255,255,255,0.05)')
    .borderRadius(12)
    .backgroundBlurStyle(BlurStyle.Thin)
    .margin({ bottom: 12 })
  }
}

/**
 * GlowBackground — 主题色光晕背景装饰
 * 用于设置页顶部装饰
 */
@Component
export struct GlowBackground {
  @Prop color: string = 'rgba(124,77,255,0.15)';
  @Prop glowSize: number = 200;

  build() {
    Column()
      .width(this.glowSize)
      .height(this.glowSize)
      .backgroundColor(this.color)
      .blur(40)
      .borderRadius(this.glowSize / 2)
      .position({ x: '10%', y: '20%' })
  }
}

/**
 * AppConfigStore — 应用配置存储封装
 * 封装 Preferences 读写，提供类型安全访问
 */
export class AppConfigStore {
  private pref?: dataPreferences.Preferences;
  private readonly storeName: string = 'trulymem_config';

  async init(ctx: Context): Promise<void> {
    this.pref = await dataPreferences.getPreferences(ctx, this.storeName);
  }

  async getString(key: string, defaultValue: string): Promise<string> {
    return String(await this.pref?.get(key, defaultValue));
  }

  async setString(key: string, value: string): Promise<void> {
    await this.pref?.put(key, value);
    await this.pref?.flush();
  }

  static async create(ctx: Context): Promise<AppConfigStore> {
    const store = new AppConfigStore();
    await store.init(ctx);
    return store;
  }
}
