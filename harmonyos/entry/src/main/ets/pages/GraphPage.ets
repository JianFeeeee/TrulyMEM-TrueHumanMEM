import web_webview from '@ohos.web.webview';
import { GraphDatabase } from '../model/GraphDatabase';

@Component
export struct GraphPage {
    private controller: web_webview.WebviewController = new web_webview.WebviewController();
    private db: GraphDatabase;

    build() {
        Column() {
            Web({ src: $rawfile('graph.html'), controller: this.controller })
                .javaScriptAccess(true)
                .onMessageReceive((msg) => {
                    if (msg.data === 'request_graph_data') {
                        this.sendGraphData();
                    }
                })
                .width('100%')
                .height('100%')
        }
        .width('100%')
        .height('100%')
    }

    async sendGraphData() {
        const result = await this.db.introspect();
        if (result.success) {
            const jsonStr = JSON.stringify(result.data);
            this.controller.runJavaScriptExt('loadGraphData(' + jsonStr + ')', (error, data) => {
                if (error) {
                    console.error('runJavaScriptExt error: ' + JSON.stringify(error));
                }
            });
        }
    }
}
