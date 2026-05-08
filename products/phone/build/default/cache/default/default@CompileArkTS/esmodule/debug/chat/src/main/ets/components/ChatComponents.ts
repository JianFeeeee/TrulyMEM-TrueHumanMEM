if (!("finalizeConstruction" in ViewPU.prototype)) {
    Reflect.set(ViewPU.prototype, "finalizeConstruction", () => { });
}
interface ChatMessageList_Params {
    messages?: ChatMessage[];
    isThinking?: boolean;
    toolCallLog?: string;
    scrollController?: Scroller;
}
interface ChatInputBar_Params {
    inputText?: string;
    isThinking?: boolean;
    onSend?: () => void;
}
interface ToolCallLogPanel_Params {
    logText?: string;
}
interface ThinkingIndicator_Params {
}
interface ChatMessageBubble_Params {
    msg?: ChatMessage;
}
import type { ChatMessage } from '@ohos/common';
export class ChatMessageBubble extends ViewPU {
    constructor(parent, params, __localStorage, elmtId = -1, paramsLambda = undefined, extraInfo) {
        super(parent, __localStorage, elmtId, extraInfo);
        if (typeof paramsLambda === "function") {
            this.paramsGenerator_ = paramsLambda;
        }
        this.__msg = new SynchedPropertyNesedObjectPU(params.msg, this, "msg");
        this.setInitiallyProvidedValue(params);
        this.finalizeConstruction();
    }
    setInitiallyProvidedValue(params: ChatMessageBubble_Params) {
        this.__msg.set(params.msg);
    }
    updateStateVars(params: ChatMessageBubble_Params) {
        this.__msg.set(params.msg);
    }
    purgeVariableDependenciesOnElmtId(rmElmtId) {
        this.__msg.purgeDependencyOnElmtId(rmElmtId);
    }
    aboutToBeDeleted() {
        this.__msg.aboutToBeDeleted();
        SubscriberManager.Get().delete(this.id__());
        this.aboutToBeDeletedInternal();
    }
    private __msg: SynchedPropertyNesedObjectPU<ChatMessage>;
    get msg() {
        return this.__msg.get();
    }
    initialRender() {
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Column.create();
            Column.padding(12);
            Column.backgroundColor(this.msg.role === 'user' ? 'rgba(124,77,255,0.15)' : 'rgba(245,245,245,0.1)');
            Column.borderRadius(12);
            Column.border({
                width: 1,
                color: this.msg.role === 'user' ? 'rgba(124,77,255,0.3)' : 'rgba(255,255,255,0.1)'
            });
            Column.backgroundBlurStyle(BlurStyle.Thin);
            Column.margin({ left: 8, right: 8, bottom: 8 });
            Column.width('100%');
            Column.alignItems(HorizontalAlign.Start);
        }, Column);
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            // 角色标识
            Text.create(this.msg.role === 'user' ? '🧑 你' : '🤖 AI');
            // 角色标识
            Text.fontSize(11);
            // 角色标识
            Text.fontColor(this.msg.role === 'user' ? '#7C4DFF' : '#999');
            // 角色标识
            Text.width('100%');
        }, Text);
        // 角色标识
        Text.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            // 消息内容
            Text.create(this.msg.content);
            // 消息内容
            Text.fontSize(15);
            // 消息内容
            Text.width('100%');
            // 消息内容
            Text.margin({ top: 4 });
            // 消息内容
            Text.fontColor('#FFFFFF');
        }, Text);
        // 消息内容
        Text.pop();
        Column.pop();
    }
    rerender() {
        this.updateDirtyElements();
    }
}
export class ThinkingIndicator extends ViewPU {
    constructor(parent, params, __localStorage, elmtId = -1, paramsLambda = undefined, extraInfo) {
        super(parent, __localStorage, elmtId, extraInfo);
        if (typeof paramsLambda === "function") {
            this.paramsGenerator_ = paramsLambda;
        }
        this.setInitiallyProvidedValue(params);
        this.finalizeConstruction();
    }
    setInitiallyProvidedValue(params: ThinkingIndicator_Params) {
    }
    updateStateVars(params: ThinkingIndicator_Params) {
    }
    purgeVariableDependenciesOnElmtId(rmElmtId) {
    }
    aboutToBeDeleted() {
        SubscriberManager.Get().delete(this.id__());
        this.aboutToBeDeletedInternal();
    }
    initialRender() {
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Row.create();
            Row.padding(12);
            Row.backgroundColor('rgba(124,77,255,0.1)');
            Row.borderRadius(12);
            Row.border({ width: 1, color: 'rgba(124,77,255,0.2)' });
            Row.backgroundBlurStyle(BlurStyle.Thin);
            Row.margin({ left: 8, right: 8, bottom: 8 });
        }, Row);
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            LoadingProgress.create();
            LoadingProgress.width(20);
            LoadingProgress.height(20);
            LoadingProgress.margin({ right: 8 });
            LoadingProgress.color('#7C4DFF');
        }, LoadingProgress);
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Text.create('AI 思考中...');
            Text.fontSize(13);
            Text.fontColor('#7C4DFF');
        }, Text);
        Text.pop();
        Row.pop();
    }
    rerender() {
        this.updateDirtyElements();
    }
}
export class ToolCallLogPanel extends ViewPU {
    constructor(parent, params, __localStorage, elmtId = -1, paramsLambda = undefined, extraInfo) {
        super(parent, __localStorage, elmtId, extraInfo);
        if (typeof paramsLambda === "function") {
            this.paramsGenerator_ = paramsLambda;
        }
        this.__logText = new SynchedPropertySimpleOneWayPU(params.logText, this, "logText");
        this.setInitiallyProvidedValue(params);
        this.finalizeConstruction();
    }
    setInitiallyProvidedValue(params: ToolCallLogPanel_Params) {
    }
    updateStateVars(params: ToolCallLogPanel_Params) {
        this.__logText.reset(params.logText);
    }
    purgeVariableDependenciesOnElmtId(rmElmtId) {
        this.__logText.purgeDependencyOnElmtId(rmElmtId);
    }
    aboutToBeDeleted() {
        this.__logText.aboutToBeDeleted();
        SubscriberManager.Get().delete(this.id__());
        this.aboutToBeDeletedInternal();
    }
    private __logText: SynchedPropertySimpleOneWayPU<string>;
    get logText() {
        return this.__logText.get();
    }
    set logText(newValue: string) {
        this.__logText.set(newValue);
    }
    initialRender() {
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Text.create(this.logText);
            Text.fontSize(10);
            Text.fontColor('#FF9800');
            Text.backgroundColor('rgba(255,152,0,0.1)');
            Text.padding(8);
            Text.borderRadius(8);
            Text.border({ width: 1, color: 'rgba(255,152,0,0.2)' });
            Text.backgroundBlurStyle(BlurStyle.Thin);
            Text.margin({ left: 8, right: 8, bottom: 4 });
            Text.lineHeight(16);
        }, Text);
        Text.pop();
    }
    rerender() {
        this.updateDirtyElements();
    }
}
export class ChatInputBar extends ViewPU {
    constructor(parent, params, __localStorage, elmtId = -1, paramsLambda = undefined, extraInfo) {
        super(parent, __localStorage, elmtId, extraInfo);
        if (typeof paramsLambda === "function") {
            this.paramsGenerator_ = paramsLambda;
        }
        this.__inputText = new SynchedPropertySimpleTwoWayPU(params.inputText, this, "inputText");
        this.__isThinking = new SynchedPropertySimpleOneWayPU(params.isThinking, this, "isThinking");
        this.onSend = undefined;
        this.setInitiallyProvidedValue(params);
        this.finalizeConstruction();
    }
    setInitiallyProvidedValue(params: ChatInputBar_Params) {
        if (params.onSend !== undefined) {
            this.onSend = params.onSend;
        }
    }
    updateStateVars(params: ChatInputBar_Params) {
        this.__isThinking.reset(params.isThinking);
    }
    purgeVariableDependenciesOnElmtId(rmElmtId) {
        this.__inputText.purgeDependencyOnElmtId(rmElmtId);
        this.__isThinking.purgeDependencyOnElmtId(rmElmtId);
    }
    aboutToBeDeleted() {
        this.__inputText.aboutToBeDeleted();
        this.__isThinking.aboutToBeDeleted();
        SubscriberManager.Get().delete(this.id__());
        this.aboutToBeDeletedInternal();
    }
    private __inputText: SynchedPropertySimpleTwoWayPU<string>;
    get inputText() {
        return this.__inputText.get();
    }
    set inputText(newValue: string) {
        this.__inputText.set(newValue);
    }
    private __isThinking: SynchedPropertySimpleOneWayPU<boolean>;
    get isThinking() {
        return this.__isThinking.get();
    }
    set isThinking(newValue: boolean) {
        this.__isThinking.set(newValue);
    }
    private onSend?: () => void;
    initialRender() {
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Row.create();
            Row.width('100%');
            Row.padding(8);
            Row.backgroundColor('rgba(255,255,255,0.05)');
            Row.backgroundBlurStyle(BlurStyle.Regular);
            Row.border({
                width: 1,
                color: 'rgba(124,77,255,0.2)',
                style: BorderStyle.Solid
            });
        }, Row);
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            TextArea.create({ text: this.inputText, placeholder: '输入消息...' });
            TextArea.layoutWeight(1);
            TextArea.onChange((v: string) => { this.inputText = v; });
            TextArea.height(40);
            TextArea.backgroundColor('rgba(255,255,255,0.1)');
            TextArea.borderRadius(8);
            TextArea.border({ width: 1, color: 'rgba(124,77,255,0.3)' });
        }, TextArea);
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Button.createWithLabel('发送');
            Button.enabled(!this.isThinking);
            Button.onClick(() => { this.onSend?.(); });
            Button.backgroundColor('#7C4DFF');
            Button.borderRadius(8);
        }, Button);
        Button.pop();
        Row.pop();
    }
    rerender() {
        this.updateDirtyElements();
    }
}
export class ChatMessageList extends ViewPU {
    constructor(parent, params, __localStorage, elmtId = -1, paramsLambda = undefined, extraInfo) {
        super(parent, __localStorage, elmtId, extraInfo);
        if (typeof paramsLambda === "function") {
            this.paramsGenerator_ = paramsLambda;
        }
        this.__messages = new SynchedPropertyObjectOneWayPU(params.messages, this, "messages");
        this.__isThinking = new SynchedPropertySimpleOneWayPU(params.isThinking, this, "isThinking");
        this.__toolCallLog = new SynchedPropertySimpleOneWayPU(params.toolCallLog, this, "toolCallLog");
        this.scrollController = new Scroller();
        this.setInitiallyProvidedValue(params);
        this.finalizeConstruction();
    }
    setInitiallyProvidedValue(params: ChatMessageList_Params) {
        if (params.scrollController !== undefined) {
            this.scrollController = params.scrollController;
        }
    }
    updateStateVars(params: ChatMessageList_Params) {
        this.__messages.reset(params.messages);
        this.__isThinking.reset(params.isThinking);
        this.__toolCallLog.reset(params.toolCallLog);
    }
    purgeVariableDependenciesOnElmtId(rmElmtId) {
        this.__messages.purgeDependencyOnElmtId(rmElmtId);
        this.__isThinking.purgeDependencyOnElmtId(rmElmtId);
        this.__toolCallLog.purgeDependencyOnElmtId(rmElmtId);
    }
    aboutToBeDeleted() {
        this.__messages.aboutToBeDeleted();
        this.__isThinking.aboutToBeDeleted();
        this.__toolCallLog.aboutToBeDeleted();
        SubscriberManager.Get().delete(this.id__());
        this.aboutToBeDeletedInternal();
    }
    private __messages: SynchedPropertySimpleOneWayPU<ChatMessage[]>;
    get messages() {
        return this.__messages.get();
    }
    set messages(newValue: ChatMessage[]) {
        this.__messages.set(newValue);
    }
    private __isThinking: SynchedPropertySimpleOneWayPU<boolean>;
    get isThinking() {
        return this.__isThinking.get();
    }
    set isThinking(newValue: boolean) {
        this.__isThinking.set(newValue);
    }
    private __toolCallLog: SynchedPropertySimpleOneWayPU<string>;
    get toolCallLog() {
        return this.__toolCallLog.get();
    }
    set toolCallLog(newValue: string) {
        this.__toolCallLog.set(newValue);
    }
    private scrollController: Scroller;
    initialRender() {
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            List.create();
            List.width('100%');
            List.layoutWeight(1);
            List.backgroundColor('rgba(0,0,0,0.1)');
        }, List);
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            ForEach.create();
            const forEachItemGenFunction = _item => {
                const msg = _item;
                {
                    const itemCreation = (elmtId, isInitialRender) => {
                        ViewStackProcessor.StartGetAccessRecordingFor(elmtId);
                        ListItem.create(deepRenderFunction, true);
                        if (!isInitialRender) {
                            ListItem.pop();
                        }
                        ViewStackProcessor.StopGetAccessRecording();
                    };
                    const itemCreation2 = (elmtId, isInitialRender) => {
                        ListItem.create(deepRenderFunction, true);
                    };
                    const deepRenderFunction = (elmtId, isInitialRender) => {
                        itemCreation(elmtId, isInitialRender);
                        {
                            this.observeComponentCreation2((elmtId, isInitialRender) => {
                                if (isInitialRender) {
                                    let componentCall = new ChatMessageBubble(this, { msg: msg }, undefined, elmtId, () => { }, { page: "features/chat/src/main/ets/components/ChatComponents.ets", line: 141, col: 11 });
                                    ViewPU.create(componentCall);
                                    let paramsLambda = () => {
                                        return {
                                            msg: msg
                                        };
                                    };
                                    componentCall.paramsGenerator_ = paramsLambda;
                                }
                                else {
                                    this.updateStateVarsOfChildByElmtId(elmtId, {
                                        msg: msg
                                    });
                                }
                            }, { name: "ChatMessageBubble" });
                        }
                        ListItem.pop();
                    };
                    this.observeComponentCreation2(itemCreation2, ListItem);
                    ListItem.pop();
                }
            };
            this.forEachUpdateFunction(elmtId, this.messages, forEachItemGenFunction);
        }, ForEach);
        ForEach.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            If.create();
            if (this.isThinking) {
                this.ifElseBranchUpdateFunction(0, () => {
                    {
                        const itemCreation = (elmtId, isInitialRender) => {
                            ViewStackProcessor.StartGetAccessRecordingFor(elmtId);
                            ListItem.create(deepRenderFunction, true);
                            if (!isInitialRender) {
                                ListItem.pop();
                            }
                            ViewStackProcessor.StopGetAccessRecording();
                        };
                        const itemCreation2 = (elmtId, isInitialRender) => {
                            ListItem.create(deepRenderFunction, true);
                        };
                        const deepRenderFunction = (elmtId, isInitialRender) => {
                            itemCreation(elmtId, isInitialRender);
                            {
                                this.observeComponentCreation2((elmtId, isInitialRender) => {
                                    if (isInitialRender) {
                                        let componentCall = new ThinkingIndicator(this, {}, undefined, elmtId, () => { }, { page: "features/chat/src/main/ets/components/ChatComponents.ets", line: 147, col: 11 });
                                        ViewPU.create(componentCall);
                                        let paramsLambda = () => {
                                            return {};
                                        };
                                        componentCall.paramsGenerator_ = paramsLambda;
                                    }
                                    else {
                                        this.updateStateVarsOfChildByElmtId(elmtId, {});
                                    }
                                }, { name: "ThinkingIndicator" });
                            }
                            ListItem.pop();
                        };
                        this.observeComponentCreation2(itemCreation2, ListItem);
                        ListItem.pop();
                    }
                });
            }
            else {
                this.ifElseBranchUpdateFunction(1, () => {
                });
            }
        }, If);
        If.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            If.create();
            if (this.toolCallLog && !this.isThinking) {
                this.ifElseBranchUpdateFunction(0, () => {
                    {
                        const itemCreation = (elmtId, isInitialRender) => {
                            ViewStackProcessor.StartGetAccessRecordingFor(elmtId);
                            ListItem.create(deepRenderFunction, true);
                            if (!isInitialRender) {
                                ListItem.pop();
                            }
                            ViewStackProcessor.StopGetAccessRecording();
                        };
                        const itemCreation2 = (elmtId, isInitialRender) => {
                            ListItem.create(deepRenderFunction, true);
                        };
                        const deepRenderFunction = (elmtId, isInitialRender) => {
                            itemCreation(elmtId, isInitialRender);
                            {
                                this.observeComponentCreation2((elmtId, isInitialRender) => {
                                    if (isInitialRender) {
                                        let componentCall = new ToolCallLogPanel(this, { logText: this.toolCallLog }, undefined, elmtId, () => { }, { page: "features/chat/src/main/ets/components/ChatComponents.ets", line: 153, col: 11 });
                                        ViewPU.create(componentCall);
                                        let paramsLambda = () => {
                                            return {
                                                logText: this.toolCallLog
                                            };
                                        };
                                        componentCall.paramsGenerator_ = paramsLambda;
                                    }
                                    else {
                                        this.updateStateVarsOfChildByElmtId(elmtId, {
                                            logText: this.toolCallLog
                                        });
                                    }
                                }, { name: "ToolCallLogPanel" });
                            }
                            ListItem.pop();
                        };
                        this.observeComponentCreation2(itemCreation2, ListItem);
                        ListItem.pop();
                    }
                });
            }
            else {
                this.ifElseBranchUpdateFunction(1, () => {
                });
            }
        }, If);
        If.pop();
        List.pop();
    }
    rerender() {
        this.updateDirtyElements();
    }
}
