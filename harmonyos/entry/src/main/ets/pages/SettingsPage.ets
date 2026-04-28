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
        Column() {
            Text('API 配置').fontSize(24).fontWeight(FontWeight.Bold).margin({ top: 20, bottom: 16 })

            Text('Base URL').fontSize(14).width('100%').margin({ left: 16 })
            TextInput({ placeholder: 'https://api.deepseek.com', text: this.baseUrl })
                .onChange((v: string) => { this.onBaseUrlChange(v); })
                .margin({ left: 16, right: 16, bottom: 12 })

            Text('Model ID').fontSize(14).width('100%').margin({ left: 16 })
            TextInput({ placeholder: 'deepseek-chat', text: this.model })
                .onChange((v: string) => { this.onModelChange(v); })
                .margin({ left: 16, right: 16, bottom: 12 })

            Text('API Key').fontSize(14).width('100%').margin({ left: 16 })
            TextInput({ placeholder: 'sk-...', text: this.apiKey })
                .type(InputType.Password)
                .onChange((v: string) => { this.onApiKeyChange(v); })
                .margin({ left: 16, right: 16, bottom: 12 })
        }
        .width('100%')
        .height('100%')
        .padding(16)
    }
}
