import { ChatMessage } from '@ohos/common';

/**
 * ChatMessageBubble — 单条聊天消息气泡
 * 封装消息的角色标识、内容样式、玻璃拟态背景
 */
@Component
export struct ChatMessageBubble {
  @ObjectLink msg: ChatMessage;

  build() {
    Column() {
      // 角色标识
      Text(this.msg.role === 'user' ? '🧑 你' : '🤖 AI')
        .fontSize(11)
        .fontColor(this.msg.role === 'user' ? '#7C4DFF' : '#999')
        .width('100%')

      // 消息内容
      Text(this.msg.content)
        .fontSize(15)
        .width('100%')
        .margin({ top: 4 })
        .fontColor('#FFFFFF')
    }
    .padding(12)
    .backgroundColor(this.msg.role === 'user' ? 'rgba(124,77,255,0.15)' : 'rgba(245,245,245,0.1)')
    .borderRadius(12)
    .border({
      width: 1,
      color: this.msg.role === 'user' ? 'rgba(124,77,255,0.3)' : 'rgba(255,255,255,0.1)'
    })
    .backgroundBlurStyle(BlurStyle.Thin)
    .margin({ left: 8, right: 8, bottom: 8 })
    .width('100%')
    .alignItems(HorizontalAlign.Start)
  }
}

/**
 * ThinkingIndicator — AI 思考中指示器
 * 玻璃拟态加载动画 + 文字提示
 */
@Component
export struct ThinkingIndicator {
  build() {
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

/**
 * ToolCallLogPanel — 工具调用日志面板
 * 橙色风格，显示 Agent 调用的工具链
 */
@Component
export struct ToolCallLogPanel {
  @Prop logText: string;

  build() {
    Text(this.logText)
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

/**
 * ChatInputBar — 底部输入栏
 * TextArea + 发送按钮，主题色边框
 */
@Component
export struct ChatInputBar {
  @Link inputText: string;
  @Prop isThinking: boolean;
  onSend?: () => void;

  build() {
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
        .onClick(() => { this.onSend?.(); })
        .backgroundColor('#7C4DFF')
        .borderRadius(8)
    }
    .width('100%')
    .padding(8)
    .backgroundColor('rgba(255,255,255,0.05)')
    .backgroundBlurStyle(BlurStyle.Regular)
    .border({
      width: 1,
      color: 'rgba(124,77,255,0.2)',
      style: BorderStyle.Solid
    })
  }
}

/**
 * ChatMessageList — 聊天消息列表容器
 * 整合消息气泡、思考指示器、工具日志
 */
@Component
export struct ChatMessageList {
  @Prop messages: ChatMessage[];
  @Prop isThinking: boolean;
  @Prop toolCallLog: string;
  private scrollController: Scroller = new Scroller();

  build() {
    List() {
      ForEach(this.messages, (msg: ChatMessage) => {
        ListItem() {
          ChatMessageBubble({ msg: msg })
        }
      })

      if (this.isThinking) {
        ListItem() {
          ThinkingIndicator()
        }
      }

      if (this.toolCallLog && !this.isThinking) {
        ListItem() {
          ToolCallLogPanel({ logText: this.toolCallLog })
        }
      }
    }
    .width('100%')
    .layoutWeight(1)
    .backgroundColor('rgba(0,0,0,0.1)')
  }
}
