// Copyright (c) 0phoff
// Distributed under the terms of the Modified BSD License.

import {
  DOMWidgetModel,
  DOMWidgetView,
  ISerializers,
} from '@jupyter-widgets/base';

import type { Polygon, PolyStyle } from './polygons';
import { centroid_polygon, inside_polygon, area_polygon } from './polygons';
import { serialize_numpy, deserialize_numpy } from './serializers';
import { MODULE_NAME, MODULE_VERSION } from './version';

export class ImageCanvasModel extends DOMWidgetModel {
  defaults() {
    return {
      ...super.defaults(),
      _model_name: ImageCanvasModel.model_name,
      _model_module: ImageCanvasModel.model_module,
      _model_module_version: ImageCanvasModel.model_module_version,
      _view_name: ImageCanvasModel.view_name,
      _view_module: ImageCanvasModel.view_module,
      _view_module_version: ImageCanvasModel.view_module_version,
    };
  }

  static serializers: ISerializers = {
    ...DOMWidgetModel.serializers,
    image: { serialize: serialize_numpy, deserialize: deserialize_numpy },
  };

  static model_name = 'ImageCanvasModel';
  static model_module = MODULE_NAME;
  static model_module_version = MODULE_VERSION;
  static view_name = 'ImageCanvasView';
  static view_module = MODULE_NAME;
  static view_module_version = MODULE_VERSION;
}

export class ImageCanvasView extends DOMWidgetView {
  private POLY: boolean;
  private ENLARGE: boolean;
  private COLOR: string;
  private ALPHA: string;
  private SIZE: number;
  private HOVER: PolyStyle;
  private CLICK: PolyStyle;

  private width: number;
  private height: number;
  private bg: HTMLCanvasElement;
  private fg: HTMLCanvasElement;
  private fx: HTMLCanvasElement;
  private result: HTMLCanvasElement;
  private poly: Polygon[];

  private scale: number;
  private offset_x: number;
  private offset_y: number;

  render() {
    // Constants
    this.POLY = this.model.get('enable_poly');
    this.ENLARGE = this.model.get('enlarge');
    this.COLOR = this.model.get('color');
    this.ALPHA = this.model.get('alpha');
    this.SIZE = this.model.get('size');
    this.HOVER = this.model.get('hover_style');
    this.CLICK = this.model.get('click_style');

    // PY -> JS
    this.model.on('change:width', this.render_children, this);
    this.model.on('change:height', this.render_children, this);
    this.model.on('change:image', this.draw_image, this);
    this.model.on('change:save', this.save, this);
    if (this.POLY) {
      this.model.on('change:polygons', this.draw_polygons, this);
      if (this.HOVER !== null) {
        this.model.on('change:hovered', this.draw_fx, this);
      }
      if (this.CLICK !== null) {
        this.model.on('change:clicked', this.draw_fx, this);
      }
    }

    // Start
    this.render_children();
  }

  render_children() {
    // Constants
    this.width = this.model.get('width') - 2;
    this.height = this.model.get('height') - 2;

    // Create elements
    this.bg = document.createElement('canvas');
    this.bg.width = this.width;
    this.bg.height = this.height;
    this.bg.style.border = '1px solid lightgray';
    this.result = document.createElement('canvas');
    this.result.width = this.width;
    this.result.height = this.height;
    if (this.POLY) {
      this.fg = document.createElement('canvas');
      this.fg.width = this.width;
      this.fg.height = this.height;
      this.fg.style.position = 'absolute';
      this.fg.style.top = '0px';
      this.fg.style.left = '0px';
      this.fg.style.right = '0px';
      this.fg.style.marginLeft = 'auto';
      this.fg.style.marginRight = 'auto';
      this.fx = document.createElement('canvas');
      this.fx.width = this.width;
      this.fx.height = this.height;
      this.fx.style.position = 'absolute';
      this.fx.style.top = '0px';
      this.fx.style.left = '0px';
      this.fx.style.right = '0px';
      this.fx.style.marginLeft = 'auto';
      this.fx.style.marginRight = 'auto';
    }

    // Add to DOM
    const div = document.createElement('div');
    div.style.textAlign = 'center';
    div.style.minWidth = this.width + 'px';
    div.style.minHeight = this.height + 'px';
    div.appendChild(this.bg);
    if (this.POLY) {
      div.appendChild(this.fg);
      div.appendChild(this.fx);
    }

    while (this.el.firstChild) {
      this.el.firstChild.remove();
    }
    this.el.appendChild(div);

    this.draw_image();
    if (this.POLY) {
      this.draw_polygons();
      this.draw_fx();
      this.fx.onclick = this.onclick.bind(this);
      this.fx.onmousemove = this.onhover.bind(this);
      this.fx.onmouseleave = () => {
        this.model.set('hovered', null);
        this.touch();
      };
    }
  }

  draw_image() {
    const img = this.model.get('image'),
      bgctx = this.bg.getContext('2d');
    if (!bgctx) {
      return;
    }

    bgctx.clearRect(0, 0, this.bg.width, this.bg.height);
    this.scale = 1;
    this.offset_x = 0;
    this.offset_y = 0;

    if (img) {
      const imgd = new ImageData(img.data, img.shape[1], img.shape[0]);

      if (
        !this.ENLARGE &&
        img.shape[1] <= this.width &&
        img.shape[0] <= this.height
      ) {
        this.offset_x = Math.floor((this.width - img.shape[1]) / 2);
        this.offset_y = Math.floor((this.height - img.shape[0]) / 2);
        bgctx.putImageData(imgd, this.offset_x, this.offset_y);
      } else {
        const oc = document.createElement('canvas'),
          octx = oc.getContext('2d');
        if (!octx) {
          return;
        }

        // Compute scale and offset
        this.scale = Math.min(
          this.width / img.shape[1],
          this.height / img.shape[0]
        );
        const scaled_w = img.shape[1] * this.scale,
          scaled_h = img.shape[0] * this.scale;

        this.offset_x = Math.floor((this.width - scaled_w) / 2);
        this.offset_y = Math.floor((this.height - scaled_h) / 2);

        // Draw original image
        oc.width = img.shape[1];
        oc.height = img.shape[0];
        octx.putImageData(imgd, 0, 0);

        // Draw rescaled image
        bgctx.drawImage(
          oc,
          0,
          0,
          img.shape[1],
          img.shape[0],
          this.offset_x,
          this.offset_y,
          scaled_w,
          scaled_h
        );
      }
    }
  }

  draw_polygons() {
    this.poly = this.model.get('polygons');
    const fgctx = this.fg.getContext('2d');
    if (!fgctx) {
      return;
    }

    fgctx.clearRect(0, 0, this.fg.width, this.fg.height);
    if (this.poly) {
      this.poly.forEach((poly) => {
        this._draw_poly(fgctx as CanvasRenderingContext2D, poly);
      });
    }
  }

  draw_fx() {
    const hover_idx = this.model.get('hovered'),
      click_idx = this.model.get('clicked'),
      fxctx = this.fx.getContext('2d');
    if (!fxctx) {
      return;
    }

    fxctx.clearRect(0, 0, this.fx.width, this.fx.height);
    if (this.poly) {
      if (hover_idx !== null && hover_idx < this.poly.length) {
        this._draw_poly(fxctx, this.poly[hover_idx], this.HOVER);
      }
      if (click_idx !== null && click_idx < this.poly.length) {
        this._draw_poly(fxctx, this.poly[click_idx], this.CLICK);
      }
    }
  }

  save() {
    const save_val = this.model.get('save');

    if (save_val) {
      const ctx = this.result.getContext('2d');
      if (!ctx) {
        return;
      }

      // Clear result canvas
      ctx.clearRect(0, 0, this.width, this.height);

      // Draw canvases
      ctx.drawImage(this.bg, 0, 0, this.width, this.height);
      if (this.POLY) {
        ctx.drawImage(this.fg, 0, 0, this.width, this.height);
        ctx.drawImage(this.fx, 0, 0, this.width, this.height);
      }

      // Open in new tab
      const data = this.result.toDataURL('png');
      const w = window.open('about:blank');
      setTimeout(() => {
        if (w) {
          w.document.body.appendChild(w.document.createElement('img')).src =
            data;
        }
      }, 0);

      // Reset save
      setTimeout(() => {
        this.model.set('save', false);
        this.model.save_changes();
      }, 0);
    }
  }

  onclick(e: MouseEvent) {
    const [x, y] = this._get_image_coord(e.clientX, e.clientY);
    this.model.set('clicked', this._get_closest_poly(x, y));
    this.touch();
  }

  onhover(e: MouseEvent) {
    const [x, y] = this._get_image_coord(e.clientX, e.clientY);
    this.model.set('hovered', this._get_closest_poly(x, y));
    this.touch();
  }

  _draw_poly(ctx: CanvasRenderingContext2D, poly: Polygon, style?: PolyStyle) {
    const coords = poly.coords.map(([x, y]) => [
      this.offset_x + x * this.scale,
      this.offset_y + y * this.scale,
    ]);

    // Draw
    ctx.beginPath();
    ctx.moveTo(coords[0][0], coords[0][1]);
    for (const [x, y] of coords.slice(1)) {
      ctx.lineTo(x, y);
    }
    ctx.closePath();

    // Styles
    if (style) {
      ctx.strokeStyle = style.color || poly.color || this.COLOR;
      ctx.lineWidth = style.size || poly.size || this.SIZE;
      ctx.fillStyle =
        ctx.strokeStyle + (style.alpha || poly.alpha || this.ALPHA);
    } else {
      ctx.strokeStyle = poly.color || this.COLOR;
      ctx.lineWidth = poly.size || this.SIZE;
      ctx.fillStyle = ctx.strokeStyle + (poly.alpha || this.ALPHA);
    }

    ctx.stroke();
    ctx.fill();
  }

  _get_image_coord(x: number, y: number) {
    const r = this.fx.getBoundingClientRect();

    x -= r.left + this.offset_x;
    y -= r.top + this.offset_y;

    x /= this.scale;
    y /= this.scale;

    return [x, y];
  }

  _get_closest_poly(x: number, y: number) {
    if (this.poly === null || this.poly.length === 0) {
      return null;
    }

    type IndexedPolygon = {
      idx: number;
      poly: Polygon;
    };
    type SmallestPolygon = IndexedPolygon & { area: number };
    type ClosestPolygon = SmallestPolygon & { distance: number };

    const candidate = this.poly
      // Remember original index
      .map((poly, idx) => {
        return { idx, poly };
      })
      // Filter boxes based on mouse position
      .filter(({ poly }) => inside_polygon([x, y], poly))
      // Reduce to find smallest box
      .reduce((smallest: SmallestPolygon[], current) => {
        const area = area_polygon(current.poly);

        if (smallest.length === 0 || area < smallest[0].area) {
          return [{ ...current, area }];
        } else if (area === smallest[0].area) {
          return [...smallest, { ...current, area }];
        }
        return smallest;
      }, [])
      // Reduce to position closest to center
      .reduce((closest: ClosestPolygon | null, current: SmallestPolygon) => {
        const [cx, cy] = centroid_polygon(current.poly);
        const distance = Math.sqrt(Math.pow(x - cx, 2) + Math.pow(y - cy, 2));

        if (closest === null || distance < closest.distance) {
          return { ...current, distance };
        }
        return closest;
      }, null);

    if (candidate === null) {
      return null;
    }
    return candidate.idx;
  }
}
