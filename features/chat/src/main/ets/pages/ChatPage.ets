import { GraphDatabase } from '@ohos/common';
import { GraphMemoryService } from '@ohos/common';
import { AIAgentService, ChatMessage, AgentResponse } from '@ohos/common';

@Component
export struct ChatPage {
    @State messages: ChatMessage[] = [];
    @State inputText: string = '';
    @Prop db: GraphDatabase;
    @State toolCallLog: string = '';
    @State isThinking: boolean = false;
    private scrollController: Scroller = new Scroller();
    private agentService?: AIAgentService;

    async aboutToAppear() {
        // 初始化图记忆服务和 Agent
        const memoryService = new GraphMemoryService(this.db);
        this.agentService = new AIAgentService(memoryService, getContext(this));

        // 加载历史消息（兼容旧数据：无 session_id 时加载全部）
        const rawHistory = await this.db.getChatHistory(50, this.agentService.getSessionId());
        if (rawHistory.length === 0) {
            // 新 session，尝试加载旧消息
            const legacyHistory = await this.db.getChatHistory(50);
            this.messages = legacyHistory.map(m => {
                const msg: ChatMessage = { role: m.role, content: m.content };
                return msg;
            });
        } else {
            this.messages = rawHistory.map(m => {
                const msg: ChatMessage = { role: m.role, content: m.content };
                return msg;
            });
        }
    }

    async sendMessage() {
        if (!this.inputText.trim() || !this.agentService) return;

        const userMessage: string = this.inputText;
        this.inputText = '';

        // 添加用户消息
        await this.db.saveChatMessage('user', userMessage, '', this.agentService.getSessionId());
        this.messages = [...this.messages, { role: 'user', content: userMessage }];

        // 显示 loading
        this.isThinking = true;
        this.toolCallLog = '';

        try {
            // 通过 Agent 发送消息
            const agentResponse: AgentResponse = await this.agentService.sendMessage(userMessage);

            // 记录工具调用日志
            if (agentResponse.toolCalls.length > 0) {
                const logs: string[] = agentResponse.toolCalls.map(tc => `🛠 ${tc.name}: ${tc.message}`);
                this.toolCallLog = logs.join('\n');
            }

            // 保存并显示 AI 回复
            await this.db.saveChatMessage('assistant', agentResponse.content, this.toolCallLog, this.agentService.getSessionId());
            this.messages = [...this.messages, { role: 'assistant', content: agentResponse.content }];
        } catch (err) {
            console.error('Agent request failed: ' + JSON.stringify(err));
            this.messages = [...this.messages, { role: 'assistant', content: `⚠️ 请求失败: ${err.message || JSON.stringify(err)}` }];
        } finally {
            this.isThinking = false;
        }
    }

    build() {
        Column() {
            // 聊天列表
            List() {
                ForEach(this.messages, (msg: ChatMessage) => {
                    ListItem() {
                        Column() {
                            // 角色标识
                            Text(msg.role === 'user' ? '🧑 你' : '🤖 AI')
                                .fontSize(11)
                                .fontColor(msg.role === 'user' ? '#7C4DFF' : '#999')
                                .width('100%')

                            // 消息内容
                            Text(msg.content)
                                .fontSize(15)
                                .width('100%')
                                .margin({ top: 4 })
                                .fontColor('#FFFFFF')
                        }
                        .padding(12)
                        .backgroundColor(msg.role === 'user' ? 'rgba(124,77,255,0.15)' : 'rgba(245,245,245,0.1)')
                        .borderRadius(12)
                        .border({ width: 1, color: msg.role === 'user' ? 'rgba(124,77,255,0.3)' : 'rgba(255,255,255,0.1)' })
                        .backgroundBlurStyle(BlurStyle.Thin)
                        .margin({ left: 8, right: 8, bottom: 8 })
                        .width('100%')
                        .alignItems(HorizontalAlign.Start)
                    }
                })

                // loading 指示
                if (this.isThinking) {
                    ListItem() {
                        Row() {
                            LoadingProgress()
                                .width(20)
                                .height(20)
                                .margin({ right: 8 })
                                .color('#7C4DFF')
                            Text('AI 思考中...')
                                .fontSize(13)
                                .fontColor('#7C4DFF')
                        }
                        .padding(12)
                        .backgroundColor('rgba(124,77,255,0.1)')
                        .borderRadius(12)
                        .border({ width: 1, color: 'rgba(124,77,255,0.2)' })
                        .backgroundBlurStyle(BlurStyle.Thin)
                        .margin({ left: 8, right: 8, bottom: 8 })
                    }
                }

                // 工具调用日志
                if (this.toolCallLog && !this.isThinking) {
                    ListItem() {
                        Text(this.toolCallLog)
                            .fontSize(10)
                            .fontColor('#FF9800')
                            .backgroundColor('rgba(255,152,0,0.1)')
                            .padding(8)
                            .borderRadius(8)
                            .border({ width: 1, color: 'rgba(255,152,0,0.2)' })
                            .backgroundBlurStyle(BlurStyle.Thin)
                            .margin({ left: 8, right: 8, bottom: 4 })
                            .lineHeight(16)
                    }
                }
            }
            .width('100%')
            .layoutWeight(1)
            .backgroundColor('rgba(0,0,0,0.1)')

            // 输入区
            Row() {
                TextArea({ text: this.inputText, placeholder: '输入消息...' })
                    .layoutWeight(1)
                    .onChange((v: string) => { this.inputText = v; })
                    .height(40)
                    .backgroundColor('rgba(255,255,255,0.1)')
                    .borderRadius(8)
                    .border({ width: 1, color: 'rgba(124,77,255,0.3)' })

                Button('发送')
                    .enabled(!this.isThinking)
                    .onClick(() => this.sendMessage())
                    .backgroundColor('#7C4DFF')
                    .borderRadius(8)
            }
            .width('100%')
            .padding(8)
            .backgroundColor('rgba(255,255,255,0.05)')
            .backgroundBlurStyle(BlurStyle.Regular)
            .border({ width: 1, color: 'rgba(124,77,255,0.2)', style: BorderStyle.Solid })
        }
        .width('100%')
        .height('100%')
        .backgroundColor('rgba(26,27,46,0.95)')
    }
}
