if (!("finalizeConstruction" in ViewPU.prototype)) {
    Reflect.set(ViewPU.prototype, "finalizeConstruction", () => { });
}
interface ChatPage_Params {
    messages?: ChatMessage[];
    inputText?: string;
    db?: GraphDatabase;
    scrollController?: Scroller;
}
import http from "@ohos:net.http";
import dataPreferences from "@ohos:data.preferences";
import type { GraphDatabase } from '../model/GraphDatabase';
interface ChatMessage {
    role: string;
    content: string;
}
export class ChatPage extends ViewPU {
    constructor(parent, params, __localStorage, elmtId = -1, paramsLambda = undefined, extraInfo) {
        super(parent, __localStorage, elmtId, extraInfo);
        if (typeof paramsLambda === "function") {
            this.paramsGenerator_ = paramsLambda;
        }
        this.__messages = new ObservedPropertyObjectPU([], this, "messages");
        this.__inputText = new ObservedPropertySimplePU('', this, "inputText");
        this.__db = new SynchedPropertyObjectOneWayPU(params.db, this, "db");
        this.scrollController = new Scroller();
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
        if (params.scrollController !== undefined) {
            this.scrollController = params.scrollController;
        }
    }
    updateStateVars(params: ChatPage_Params) {
        this.__db.reset(params.db);
    }
    purgeVariableDependenciesOnElmtId(rmElmtId) {
        this.__messages.purgeDependencyOnElmtId(rmElmtId);
        this.__inputText.purgeDependencyOnElmtId(rmElmtId);
        this.__db.purgeDependencyOnElmtId(rmElmtId);
    }
    aboutToBeDeleted() {
        this.__messages.aboutToBeDeleted();
        this.__inputText.aboutToBeDeleted();
        this.__db.aboutToBeDeleted();
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
    private scrollController: Scroller;
    async aboutToAppear() {
        this.messages = await this.db.getChatHistory(50);
    }
    async sendMessage() {
        if (!this.inputText.trim())
            return;
        const userMessage: string = this.inputText;
        this.inputText = '';
        await this.db.saveChatMessage('user', userMessage);
        const userMsg: ChatMessage = { role: 'user', content: userMessage };
        this.messages = [...this.messages, userMsg];
        const pref: dataPreferences.Preferences = await dataPreferences.getPreferences(getContext(this), 'trulymem_config');
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
        }
        catch (err) {
            console.error('HTTP request failed: ' + JSON.stringify(err));
        }
    }
    initialRender() {
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Column.create();
            Column.width('100%');
            Column.height('100%');
        }, Column);
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            List.create();
            List.width('100%');
            List.layoutWeight(1);
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
                        this.observeComponentCreation2((elmtId, isInitialRender) => {
                            Column.create();
                            Column.padding(12);
                            Column.backgroundColor(msg.role === 'user' ? '#E3F2FD' : '#F5F5F5');
                            Column.borderRadius(8);
                            Column.margin({ left: 8, right: 8, bottom: 8 });
                        }, Column);
                        this.observeComponentCreation2((elmtId, isInitialRender) => {
                            Text.create(msg.role);
                            Text.fontSize(12);
                            Text.fontColor('#666');
                            Text.width('100%');
                        }, Text);
                        Text.pop();
                        this.observeComponentCreation2((elmtId, isInitialRender) => {
                            Text.create(msg.content);
                            Text.fontSize(16);
                            Text.width('100%');
                            Text.margin({ top: 4 });
                        }, Text);
                        Text.pop();
                        Column.pop();
                        ListItem.pop();
                    };
                    this.observeComponentCreation2(itemCreation2, ListItem);
                    ListItem.pop();
                }
            };
            this.forEachUpdateFunction(elmtId, this.messages, forEachItemGenFunction);
        }, ForEach);
        ForEach.pop();
        List.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Row.create();
            Row.width('100%');
            Row.padding(8);
        }, Row);
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            TextArea.create({ text: this.inputText, placeholder: '输入消息...' });
            TextArea.layoutWeight(1);
            TextArea.onChange((v: string) => { this.inputText = v; });
        }, TextArea);
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Button.createWithLabel('发送');
            Button.onClick(() => this.sendMessage());
        }, Button);
        Button.pop();
        Row.pop();
        Column.pop();
    }
    rerender() {
        this.updateDirtyElements();
    }
}
