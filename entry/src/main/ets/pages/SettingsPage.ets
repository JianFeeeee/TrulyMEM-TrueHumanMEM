import dataPreferences from '@ohos.data.preferences';

@Component
export struct SettingsPage {
    @State baseUrl: string = '';
    @State model: string = '';
    @State apiKey: string = '';
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

    build() {
        Stack() {
            // 主题色光晕背景
            Column()
                .width(200)
                .height(200)
                .backgroundColor('rgba(124,77,255,0.15)')
                .blur(40)
                .borderRadius(100)
                .position({ x: '10%', y: '20%' })

            Column() {
                Text('API 配置')
                    .fontSize(24)
                    .fontWeight(FontWeight.Bold)
                    .fontColor('#FFFFFF')
                    .margin({ top: 20, bottom: 16 })

                // Base URL 设置项
                Column() {
                    Text('Base URL')
                        .fontSize(14)
                        .fontColor('#FFFFFF')
                        .width('100%')
                        .margin({ bottom: 8 })

                    TextInput({ placeholder: 'https://api.deepseek.com', text: this.baseUrl })
                        .onChange((v: string) => { this.onBaseUrlChange(v); })
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

                // Model ID 设置项
                Column() {
                    Text('Model ID')
                        .fontSize(14)
                        .fontColor('#FFFFFF')
                        .width('100%')
                        .margin({ bottom: 8 })

                    TextInput({ placeholder: 'deepseek-chat', text: this.model })
                        .onChange((v: string) => { this.onModelChange(v); })
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

                // API Key 设置项
                Column() {
                    Text('API Key')
                        .fontSize(14)
                        .fontColor('#FFFFFF')
                        .width('100%')
                        .margin({ bottom: 8 })

                    TextInput({ placeholder: 'sk-...', text: this.apiKey })
                        .type(InputType.Password)
                        .onChange((v: string) => { this.onApiKeyChange(v); })
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
            .padding(16)
            .width('100%')
        }
        .width('100%')
        .height('100%')
        .backgroundColor('rgba(26,27,46,0.95)')
        .backgroundBlurStyle(BlurStyle.Regular)
    }
}
