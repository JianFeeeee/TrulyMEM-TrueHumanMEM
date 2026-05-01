import { GraphDatabase, GraphMemoryService, AIAgentService, ChatMessage, AgentResponse, Logger } from '@ohos/common';
import { ChatMessageList, ChatInputBar } from '../components/ChatComponents';

@Component
export struct ChatPage {
    @State messages: ChatMessage[] = [];
    @State inputText: string = '';
    @Prop db: GraphDatabase;
    @State toolCallLog: string = '';
    @State isThinking: boolean = false;
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
            Logger.error('Agent request failed: ' + JSON.stringify(err));
            this.messages = [...this.messages, { role: 'assistant', content: `⚠️ 请求失败: ${err.message || JSON.stringify(err)}` }];
        } finally {
            this.isThinking = false;
        }
    }

    build() {
        Column() {
            ChatMessageList({
                messages: this.messages,
                isThinking: this.isThinking,
                toolCallLog: this.toolCallLog
            })

            ChatInputBar({
                inputText: this.inputText,
                isThinking: this.isThinking,
                onSend: (): void => { this.sendMessage(); }
            })
        }
        .width('100%')
        .height('100%')
        .backgroundColor('rgba(26,27,46,0.95)')
    }
}