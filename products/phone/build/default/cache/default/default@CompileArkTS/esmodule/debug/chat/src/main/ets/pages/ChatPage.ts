if (!("finalizeConstruction" in ViewPU.prototype)) {
    Reflect.set(ViewPU.prototype, "finalizeConstruction", () => { });
}
interface ChatPage_Params {
    messages?: ChatMessage[];
    inputText?: string;
    db?: GraphDatabase;
    toolCallLog?: string;
    isThinking?: boolean;
    agentService?: AIAgentService;
}
import { GraphMemoryService, AIAgentService, Logger } from "@normalized:N&&&@ohos/common/Index&1.0.0";
import type { GraphDatabase, ChatMessage, AgentResponse } from "@normalized:N&&&@ohos/common/Index&1.0.0";
import { ChatMessageList, ChatInputBar } from "@normalized:N&&&@ohos/chat/src/main/ets/components/ChatComponents&1.0.0";
export class ChatPage extends ViewPU {
    constructor(parent, params, __localStorage, elmtId = -1, paramsLambda = undefined, extraInfo) {
        super(parent, __localStorage, elmtId, extraInfo);
        if (typeof paramsLambda === "function") {
            this.paramsGenerator_ = paramsLambda;
        }
        this.__messages = new ObservedPropertyObjectPU([], this, "messages");
        this.__inputText = new ObservedPropertySimplePU('', this, "inputText");
        this.__db = new SynchedPropertyObjectOneWayPU(params.db, this, "db");
        this.__toolCallLog = new ObservedPropertySimplePU('', this, "toolCallLog");
        this.__isThinking = new ObservedPropertySimplePU(false, this, "isThinking");
        this.agentService = undefined;
        this.setInitiallyProvidedValue(params);
        this.finalizeConstruction();
    }
    setInitiallyProvidedValue(params: ChatPage_Params) {
        if (params.messages !== undefined) {
            this.messages = params.messages;
        }
        if (params.inputText !== undefined) {
            this.inputText = params.inputText;
        }
        if (params.toolCallLog !== undefined) {
            this.toolCallLog = params.toolCallLog;
        }
        if (params.isThinking !== undefined) {
            this.isThinking = params.isThinking;
        }
        if (params.agentService !== undefined) {
            this.agentService = params.agentService;
        }
    }
    updateStateVars(params: ChatPage_Params) {
        this.__db.reset(params.db);
    }
    purgeVariableDependenciesOnElmtId(rmElmtId) {
        this.__messages.purgeDependencyOnElmtId(rmElmtId);
        this.__inputText.purgeDependencyOnElmtId(rmElmtId);
        this.__db.purgeDependencyOnElmtId(rmElmtId);
        this.__toolCallLog.purgeDependencyOnElmtId(rmElmtId);
        this.__isThinking.purgeDependencyOnElmtId(rmElmtId);
    }
    aboutToBeDeleted() {
        this.__messages.aboutToBeDeleted();
        this.__inputText.aboutToBeDeleted();
        this.__db.aboutToBeDeleted();
        this.__toolCallLog.aboutToBeDeleted();
        this.__isThinking.aboutToBeDeleted();
        SubscriberManager.Get().delete(this.id__());
        this.aboutToBeDeletedInternal();
    }
    private __messages: ObservedPropertyObjectPU<ChatMessage[]>;
    get messages() {
        return this.__messages.get();
    }
    set messages(newValue: ChatMessage[]) {
        this.__messages.set(newValue);
    }
    private __inputText: ObservedPropertySimplePU<string>;
    get inputText() {
        return this.__inputText.get();
    }
    set inputText(newValue: string) {
        this.__inputText.set(newValue);
    }
    private __db: SynchedPropertySimpleOneWayPU<GraphDatabase>;
    get db() {
        return this.__db.get();
    }
    set db(newValue: GraphDatabase) {
        this.__db.set(newValue);
    }
    private __toolCallLog: ObservedPropertySimplePU<string>;
    get toolCallLog() {
        return this.__toolCallLog.get();
    }
    set toolCallLog(newValue: string) {
        this.__toolCallLog.set(newValue);
    }
    private __isThinking: ObservedPropertySimplePU<boolean>;
    get isThinking() {
        return this.__isThinking.get();
    }
    set isThinking(newValue: boolean) {
        this.__isThinking.set(newValue);
    }
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
        }
        else {
            this.messages = rawHistory.map(m => {
                const msg: ChatMessage = { role: m.role, content: m.content };
                return msg;
            });
        }
    }
    async sendMessage() {
        if (!this.inputText.trim() || !this.agentService)
            return;
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
        }
        catch (err) {
            Logger.error('Agent request failed: ' + JSON.stringify(err));
            const errMsg = (err as Error).message || JSON.stringify(err);
            this.messages = [...this.messages, { role: 'assistant', content: `⚠️ 请求失败: ${errMsg}` }];
        }
        finally {
            this.isThinking = false;
        }
    }
    initialRender() {
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Column.create();
            Column.width('100%');
            Column.height('100%');
            Column.backgroundColor('rgba(26,27,46,0.95)');
        }, Column);
        {
            this.observeComponentCreation2((elmtId, isInitialRender) => {
                if (isInitialRender) {
                    let componentCall = new ChatMessageList(this, {
                        messages: this.messages,
                        isThinking: this.isThinking,
                        toolCallLog: this.toolCallLog
                    }, undefined, elmtId, () => { }, { page: "features/chat/src/main/ets/pages/ChatPage.ets", line: 73, col: 13 });
                    ViewPU.create(componentCall);
                    let paramsLambda = () => {
                        return {
                            messages: this.messages,
                            isThinking: this.isThinking,
                            toolCallLog: this.toolCallLog
                        };
                    };
                    componentCall.paramsGenerator_ = paramsLambda;
                }
                else {
                    this.updateStateVarsOfChildByElmtId(elmtId, {
                        messages: this.messages,
                        isThinking: this.isThinking,
                        toolCallLog: this.toolCallLog
                    });
                }
            }, { name: "ChatMessageList" });
        }
        {
            this.observeComponentCreation2((elmtId, isInitialRender) => {
                if (isInitialRender) {
                    let componentCall = new ChatInputBar(this, {
                        inputText: this.__inputText,
                        isThinking: this.isThinking,
                        onSend: (): void => { this.sendMessage(); }
                    }, undefined, elmtId, () => { }, { page: "features/chat/src/main/ets/pages/ChatPage.ets", line: 79, col: 13 });
                    ViewPU.create(componentCall);
                    let paramsLambda = () => {
                        return {
                            inputText: this.inputText,
                            isThinking: this.isThinking,
                            onSend: (): void => { this.sendMessage(); }
                        };
                    };
                    componentCall.paramsGenerator_ = paramsLambda;
                }
                else {
                    this.updateStateVarsOfChildByElmtId(elmtId, {
                        isThinking: this.isThinking
                    });
                }
            }, { name: "ChatInputBar" });
        }
        Column.pop();
    }
    rerender() {
        this.updateDirtyElements();
    }
}
