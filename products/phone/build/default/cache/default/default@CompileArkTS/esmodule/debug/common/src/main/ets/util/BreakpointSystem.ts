export enum WidthBreakpoint {
    WIDTH_XS = "xs",
    WIDTH_SM = "sm",
    WIDTH_MD = "md",
    WIDTH_LG = "lg",
    WIDTH_XL = "xl"
}
export interface BreakpointTypes<T> {
    xs?: T;
    sm: T;
    md: T;
    lg: T;
    xl?: T;
}
export class BreakpointType<T> {
    private xs: T;
    private sm: T;
    private md: T;
    private lg: T;
    private xl: T;
    public constructor(param: BreakpointTypes<T>) {
        this.xs = param.xs ?? param.sm;
        this.sm = param.sm;
        this.md = param.md;
        this.lg = param.lg;
        this.xl = param.xl ?? param.lg;
    }
    public getValue(currentBreakpoint: WidthBreakpoint): T {
        if (currentBreakpoint === WidthBreakpoint.WIDTH_XS) {
            return this.xs;
        }
        if (currentBreakpoint === WidthBreakpoint.WIDTH_SM) {
            return this.sm;
        }
        if (currentBreakpoint === WidthBreakpoint.WIDTH_MD) {
            return this.md;
        }
        if (currentBreakpoint === WidthBreakpoint.WIDTH_XL) {
            return this.xl;
        }
        return this.lg;
    }
}
