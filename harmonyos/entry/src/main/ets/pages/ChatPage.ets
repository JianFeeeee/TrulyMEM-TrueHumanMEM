import http from '@ohos.net.http';
import dataPreferences from '@ohos.data.preferences';
import { GraphDatabase, ChatMessage } from '../model/GraphDatabase';

@Component
export struct ChatPage {
    @State messages: ChatMessage[] = [];
    @State inputText: string = '';
    private db: GraphDatabase;
    private scroller: Scroller = new Scroller();

    aboutToAppear() {
        this.loadHistory();
    }

    async loadHistory() {
        this.messages = await this.db.getChatHistory(50);
    }

    async sendMessage() {
        if (!this.inputText.trim()) {
            return;
        }

        const userMsg = this.inputText;
        this.inputText = '';

        // Save user message
        await this.db.saveChatMessage('user', userMsg);

        // Update UI immediately
        this.messages = await this.db.getChatHistory(50);

        // Call AI API
        try {
            const reply = await this.callAIApi(userMsg);
            await this.db.saveChatMessage('assistant', reply);
            this.messages = await this.db.getChatHistory(50);
        } catch (e) {
            await this.db.saveChatMessage('assistant', `Error: ${e.message || e}`);
            this.messages = await this.db.getChatHistory(50);
        }
    }

    async callAIApi(prompt: string): Promise<string> {
        const ctx = getContext(this);
        const pref = await dataPreferences.getPreferences(ctx, 'trulymem_config');
        const baseUrl = await pref.get('base_url', 'https://api.deepseek.com');
        const model = await pref.get('model', 'deepseek-chat');
        const apiKey = await pref.get('api_key', '');

        if (!apiKey) {
            return '请先在设置页面配置 API Key';
        }

        const httpRequest = http.createHttp();

        // Build chat history context
        const history = this.messages.slice(-10);
        const msgs = history.map(m => ({
            role: m.role,
            content: m.content,
        }));

        // Add current prompt
        msgs.push({ role: 'user', content: prompt });

        try {
            const response = await httpRequest.request(
                baseUrl.replace(/\/$/, '') + '/v1/chat/completions',
                {
                    method: http.RequestMethod.POST,
                    header: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + apiKey,
                    },
                    extraData: JSON.stringify({
                        model: model,
                        messages: msgs,
                        max_tokens: 2048,
                        stream: false,
                    }),
                    connectTimeout: 30000,
                    readTimeout: 60000,
                }
            );

            httpRequest.destroy();

            const statusCode = response.responseCode;
            if (statusCode !== 200) {
                return `API 请求失败 (${statusCode}): ${response.result.toString()}`;
            }

            const data = JSON.parse(response.result.toString());
            if (data.choices && data.choices.length > 0) {
                return data.choices[0].message.content;
            }
            return 'AI 返回为空';
        } catch (e) {
            httpRequest.destroy();
            throw e;
        }
    }

    build() {
        Column() {
            // Message list
            List({ scroller: this.scroller }) {
                ForEach(this.messages, (msg: ChatMessage) => {
                    ListItem() {
                        if (msg.role === 'user') {
                            Row() {
                                Blank()
                                Column() {
                                    Text(msg.content)
                                        .fontSize(16)
                                        .fontColor('#ffffff')
                                        .padding(12)
                                }
                                .backgroundColor('#0052cc')
                                .borderRadius(12)
                                .maxWidth('80%')
                            }
                            .width('100%')
                            .padding({ left: 16, right: 16, top: 4, bottom: 4 })
                        } else {
                            Row() {
                                Column() {
                                    Text(msg.content)
                                        .fontSize(16)
                                        .fontColor('#e0e0e0')
                                        .padding(12)
                                }
                                .backgroundColor('#2d2d3a')
                                .borderRadius(12)
                                .maxWidth('80%')
                                Blank()
                            }
                            .width('100%')
                            .padding({ left: 16, right: 16, top: 4, bottom: 4 })
                        }
                    }
                }, (msg: ChatMessage) => msg.id.toString())
            }
            .width('100%')
            .layoutWeight(1)

            // Input area
            Row() {
                TextArea({ text: this.inputText, placeholder: '输入消息...' })
                    .layoutWeight(1)
                    .maxLines(4)
                    .onChange((v: string) => {
                        this.inputText = v;
                    })
                    .margin({ left: 8, right: 4 })
                    .backgroundColor('#1e1e2e')
                    .fontColor('#ffffff')

                Button('发送')
                    .onClick(() => this.sendMessage())
                    .margin({ left: 4, right: 8 })
                    .backgroundColor('#0052cc')
            }
            .width('100%')
            .height(64)
            .backgroundColor('#16162a')
            .padding({ top: 8, bottom: 8 })
        }
        .width('100%')
        .height('100%')
        .backgroundColor('#0a0a1a')
    }
}
