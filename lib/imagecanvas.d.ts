import { DOMWidgetModel, DOMWidgetView, ISerializers } from '@jupyter-widgets/base';
import type { Polygon, PolyStyle } from './polygons';
export declare class ImageCanvasModel extends DOMWidgetModel {
    defaults(): any;
    static serializers: ISerializers;
    static model_name: string;
    static model_module: any;
    static model_module_version: any;
    static view_name: string;
    static view_module: any;
    static view_module_version: any;
}
export declare class ImageCanvasView extends DOMWidgetView {
    private POLY;
    private ENLARGE;
    private COLOR;
    private ALPHA;
    private SIZE;
    private HOVER;
    private CLICK;
    private width;
    private height;
    private bg;
    private fg;
    private fx;
    private result;
    private poly;
    private scale;
    private offset_x;
    private offset_y;
    render(): void;
    render_children(): void;
    draw_image(): void;
    draw_polygons(): void;
    draw_fx(): void;
    save(): void;
    onclick(e: MouseEvent): void;
    onhover(e: MouseEvent): void;
    _draw_poly(ctx: CanvasRenderingContext2D, poly: Polygon, style?: PolyStyle): void;
    _get_image_coord(x: number, y: number): number[];
    _get_closest_poly(x: number, y: number): number | null;
}
