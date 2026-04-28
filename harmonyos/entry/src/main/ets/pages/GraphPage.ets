import web_webview from '@ohos.web.webview';
import { GraphDatabase } from '../model/GraphDatabase';

@Component
export struct GraphPage {
    private controller: web_webview.WebviewController = new web_webview.WebviewController();
    @Prop db: GraphDatabase;

    build() {
        Column() {
            Web({ src: $rawfile('graph.html'), controller: this.controller })
                .javaScriptAccess(true)
                .width('100%')
                .height('100%')
        }
        .width('100%')
        .height('100%')
        .onAppear(() => {
            this.controller.refresh();
        })
    }
}
