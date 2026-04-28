import http from '@ohos.net.http';
import dataPreferences from '@ohos.data.preferences';
import { GraphDatabase } from '../model/GraphDatabase';

interface ChatMessage {
    role: string;
    content: string;
}

@Component
export struct ChatPage {
    @State messages: ChatMessage[] = [];
    @State inputText: string = '';
    @Prop db: GraphDatabase;
    private scrollController: Scroller = new Scroller();

    async aboutToAppear() {
        this.messages = await this.db.getChatHistory(50);
    }

    async sendMessage() {
        if (!this.inputText.trim()) return;

        const userMessage: string = this.inputText;
        this.inputText = '';

        await this.db.saveChatMessage('user', userMessage);
        const userMsg: ChatMessage = { role: 'user', content: userMessage };
        this.messages = [...this.messages, userMsg];

        const pref: dataPreferences.Preferences =
            await dataPreferences.getPreferences(getContext(this), 'trulymem_config');
        const baseUrl: string = String(await pref.get('base_url', 'https://api.deepseek.com'));
        const model: string = String(await pref.get('model', 'deepseek-chat'));
        const apiKey: string = String(await pref.get('api_key', ''));

        try {
            const httpRequest: http.HttpRequest = http.createHttp();
            const response: http.HttpResponse = await httpRequest.request(baseUrl + '/chat/completions', {
                method: http.RequestMethod.POST,
                header: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + apiKey
                },
                extraData: {
                    model: model,
                    messages: [{ role: 'user', content: userMessage }]
                }
            });

            if (response.responseCode === 200) {
                const data: object = JSON.parse(String(response.result));
                const choicesArr: object[] = data['choices'] as object[];
                if (choicesArr && choicesArr.length > 0) {
                    const firstChoice: object = choicesArr[0];
                    const msgObj: object = firstChoice['message'] as object;
                    const assistantMessage: string = String(msgObj['content']);
                    await this.db.saveChatMessage('assistant', assistantMessage);
                    const aiMsg: ChatMessage = { role: 'assistant', content: assistantMessage };
                    this.messages = [...this.messages, aiMsg];
                }
            }
        } catch (err) {
            console.error('HTTP request failed: ' + JSON.stringify(err));
        }
    }

    build() {
        Column() {
            List() {
                ForEach(this.messages, (msg: ChatMessage) => {
                    ListItem() {
                        Column() {
                            Text(msg.role).fontSize(12).fontColor('#666').width('100%')
                            Text(msg.content).fontSize(16).width('100%').margin({ top: 4 })
                        }
                        .padding(12)
                        .backgroundColor(msg.role === 'user' ? '#E3F2FD' : '#F5F5F5')
                        .borderRadius(8)
                        .margin({ left: 8, right: 8, bottom: 8 })
                    }
                })
            }
            .width('100%')
            .layoutWeight(1)

            Row() {
                TextArea({ text: this.inputText, placeholder: '输入消息...' })
                    .layoutWeight(1)
                    .onChange((v: string) => { this.inputText = v; })
                Button('发送')
                    .onClick(() => this.sendMessage())
            }
            .width('100%')
            .padding(8)
        }
        .width('100%')
        .height('100%')
    }
}
