import relationalStore from '@ohos.data.relationalStore';
import { Context } from '@ohos.abilityAccessCtrl';

const STORE_CONFIG: relationalStore.StoreConfig = {
    name: 'trulymem.db',
    securityLevel: relationalStore.SecurityLevel.S1
};

export class GraphDatabase {
    private store?: relationalStore.RdbStore;
    private context?: Context;

    async init(context: Context) {
        this.context = context;
        this.store = await relationalStore.getRdbStore(context, STORE_CONFIG);
    }

    getStore(): relationalStore.RdbStore | undefined {
        return this.store;
    }
}
