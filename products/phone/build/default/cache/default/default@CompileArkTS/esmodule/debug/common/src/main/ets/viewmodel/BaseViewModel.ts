import { WidthBreakpoint } from "@normalized:N&&&@ohos/common/src/main/ets/util/BreakpointSystem&1.0.0";
export interface VMEvent {
}
export class BaseViewModel {
    protected isAttached: boolean = false;
    protected isDisposed: boolean = false;
    protected currentBreakpoint: WidthBreakpoint = WidthBreakpoint.WIDTH_MD;
    attach(): void {
        if (this.isAttached) {
            return;
        }
        this.isAttached = true;
        this.onAttach();
    }
    detach(): void {
        if (!this.isAttached) {
            return;
        }
        this.isAttached = false;
        this.onDetach();
    }
    dispose(): void {
        if (this.isDisposed) {
            return;
        }
        this.isDisposed = true;
        this.detach();
        this.onDispose();
    }
    protected onAttach(): void {
    }
    protected onDetach(): void {
    }
    protected onDispose(): void {
    }
    public get attached(): boolean {
        return this.isAttached;
    }
    public get disposed(): boolean {
        return this.isDisposed;
    }
}
