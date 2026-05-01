import dataPreferences from '@ohos.data.preferences';
import { SettingsSectionHeader, SettingInputItem, GlowBackground, AppConfigStore } from '../components/SettingsComponents';

@Component
export struct SettingsPage {
    @State baseUrl: string = '';
    @State model: string = '';
    @State apiKey: string = '';
    private store: AppConfigStore = new AppConfigStore();

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

    build() {
        Stack() {
            GlowBackground()

            Column() {
                SettingsSectionHeader({ title: 'API 配置' })

                SettingInputItem({
                    label: 'Base URL',
                    placeholder: 'https://api.deepseek.com',
                    value: this.baseUrl,
                    onValueChange: (v: string): void => { this.saveConfig('base_url', v); }
                })

                SettingInputItem({
                    label: 'Model ID',
                    placeholder: 'deepseek-chat',
                    value: this.model,
                    onValueChange: (v: string): void => { this.saveConfig('model', v); }
                })

                SettingInputItem({
                    label: 'API Key',
                    placeholder: 'sk-...',
                    value: this.apiKey,
                    isPassword: true,
                    onValueChange: (v: string): void => { this.saveConfig('api_key', v); }
                })
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
