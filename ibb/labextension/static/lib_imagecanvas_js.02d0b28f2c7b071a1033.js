"use strict";
(self["webpackChunkibb"] = self["webpackChunkibb"] || []).push([["lib_imagecanvas_js"],{

/***/ "./lib/imagecanvas.js":
/*!****************************!*\
  !*** ./lib/imagecanvas.js ***!
  \****************************/
/***/ ((__unused_webpack_module, exports, __webpack_require__) => {


// Copyright (c) 0phoff
// Distributed under the terms of the Modified BSD License.
Object.defineProperty(exports, "__esModule", ({ value: true }));
exports.ImageCanvasView = exports.ImageCanvasModel = void 0;
const base_1 = __webpack_require__(/*! @jupyter-widgets/base */ "webpack/sharing/consume/default/@jupyter-widgets/base");
const polygons_1 = __webpack_require__(/*! ./polygons */ "./lib/polygons.js");
const serializers_1 = __webpack_require__(/*! ./serializers */ "./lib/serializers.js");
const version_1 = __webpack_require__(/*! ./version */ "./lib/version.js");
class ImageCanvasModel extends base_1.DOMWidgetModel {
    defaults() {
        return Object.assign(Object.assign({}, super.defaults()), { _model_name: ImageCanvasModel.model_name, _model_module: ImageCanvasModel.model_module, _model_module_version: ImageCanvasModel.model_module_version, _view_name: ImageCanvasModel.view_name, _view_module: ImageCanvasModel.view_module, _view_module_version: ImageCanvasModel.view_module_version });
    }
}
exports.ImageCanvasModel = ImageCanvasModel;
ImageCanvasModel.serializers = Object.assign(Object.assign({}, base_1.DOMWidgetModel.serializers), { image: { serialize: serializers_1.serialize_numpy, deserialize: serializers_1.deserialize_numpy } });
ImageCanvasModel.model_name = 'ImageCanvasModel';
ImageCanvasModel.model_module = version_1.MODULE_NAME;
ImageCanvasModel.model_module_version = version_1.MODULE_VERSION;
ImageCanvasModel.view_name = 'ImageCanvasView';
ImageCanvasModel.view_module = version_1.MODULE_NAME;
ImageCanvasModel.view_module_version = version_1.MODULE_VERSION;
class ImageCanvasView extends base_1.DOMWidgetView {
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
            if (this.HOVER != null)
                this.model.on('change:hovered', this.draw_fx, this);
            if (this.CLICK != null)
                this.model.on('change:clicked', this.draw_fx, this);
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
        var div = document.createElement('div');
        div.style.textAlign = 'center';
        div.style.minWidth = this.width + 'px';
        div.style.minHeight = this.height + 'px';
        div.appendChild(this.bg);
        if (this.POLY) {
            div.appendChild(this.fg);
            div.appendChild(this.fx);
        }
        while (this.el.firstChild)
            this.el.firstChild.remove();
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
        var img = this.model.get('image'), bgctx = this.bg.getContext('2d');
        if (!bgctx) {
            return;
        }
        bgctx.clearRect(0, 0, this.bg.width, this.bg.height);
        this.scale = 1;
        this.offset_x = 0;
        this.offset_y = 0;
        if (img) {
            var imgd = new ImageData(img.data, img.shape[1], img.shape[0]);
            if (!this.ENLARGE && img.shape[1] <= this.width && img.shape[0] <= this.height) {
                this.offset_x = Math.floor((this.width - img.shape[1]) / 2);
                this.offset_y = Math.floor((this.height - img.shape[0]) / 2);
                bgctx.putImageData(imgd, this.offset_x, this.offset_y);
            }
            else {
                var oc = document.createElement('canvas'), octx = oc.getContext('2d');
                if (!octx) {
                    return;
                }
                // Compute scale and offset
                this.scale = Math.min(this.width / img.shape[1], this.height / img.shape[0]);
                var scaled_w = img.shape[1] * this.scale, scaled_h = img.shape[0] * this.scale;
                this.offset_x = Math.floor((this.width - scaled_w) / 2);
                this.offset_y = Math.floor((this.height - scaled_h) / 2);
                // Draw original image
                oc.width = img.shape[1];
                oc.height = img.shape[0];
                octx.putImageData(imgd, 0, 0);
                // Draw rescaled image
                bgctx.drawImage(oc, 0, 0, img.shape[1], img.shape[0], this.offset_x, this.offset_y, scaled_w, scaled_h);
            }
        }
    }
    draw_polygons() {
        this.poly = this.model.get('polygons');
        var fgctx = this.fg.getContext('2d');
        if (!fgctx) {
            return;
        }
        fgctx.clearRect(0, 0, this.fg.width, this.fg.height);
        if (this.poly)
            this.poly.forEach(poly => { this._draw_poly(fgctx, poly); });
    }
    draw_fx() {
        var hover_idx = this.model.get('hovered'), click_idx = this.model.get('clicked'), fxctx = this.fx.getContext('2d');
        if (!fxctx) {
            return;
        }
        fxctx.clearRect(0, 0, this.fx.width, this.fx.height);
        if (this.poly) {
            if (hover_idx != null && hover_idx < this.poly.length) {
                this._draw_poly(fxctx, this.poly[hover_idx], this.HOVER);
            }
            if (click_idx != null && click_idx < this.poly.length) {
                this._draw_poly(fxctx, this.poly[click_idx], this.CLICK);
            }
        }
    }
    save() {
        var save_val = this.model.get('save');
        if (save_val) {
            var ctx = this.result.getContext('2d');
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
            var data = this.result.toDataURL('png');
            var w = window.open('about:blank');
            setTimeout(function () {
                if (w) {
                    w.document.body.appendChild(w.document.createElement('img')).src = data;
                }
            }, 0);
            // Reset save
            setTimeout(() => {
                this.model.set('save', false);
                this.model.save_changes();
            }, 0);
        }
    }
    onclick(e) {
        var [x, y] = this._get_image_coord(e.clientX, e.clientY);
        this.model.set('clicked', this._get_closest_poly(x, y));
        this.touch();
    }
    onhover(e) {
        var [x, y] = this._get_image_coord(e.clientX, e.clientY);
        this.model.set('hovered', this._get_closest_poly(x, y));
        this.touch();
    }
    _draw_poly(ctx, poly, style) {
        const coords = poly.coords.map(([x, y]) => [
            this.offset_x + (x * this.scale),
            this.offset_y + (y * this.scale)
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
            ctx.fillStyle = ctx.strokeStyle + (style.alpha || poly.alpha || this.ALPHA);
        }
        else {
            ctx.strokeStyle = poly.color || this.COLOR;
            ctx.lineWidth = poly.size || this.SIZE;
            ctx.fillStyle = ctx.strokeStyle + (poly.alpha || this.ALPHA);
        }
        ctx.stroke();
        ctx.fill();
    }
    _get_image_coord(x, y) {
        var r = this.fx.getBoundingClientRect();
        x -= r.left + this.offset_x;
        y -= r.top + this.offset_y;
        x /= this.scale;
        y /= this.scale;
        return [x, y];
    }
    _get_closest_poly(x, y) {
        if (this.poly === null || this.poly.length === 0)
            return null;
        var candidate = (this.poly
            // Remember original index
            .map((poly, idx) => { return { idx, poly }; })
            // Filter boxes based on mouse position
            .filter(({ poly }) => polygons_1.inside_polygon([x, y], poly))
            // Reduce to find smallest box
            .reduce((smallest, current) => {
            const area = polygons_1.area_polygon(current.poly);
            if ((smallest.length === 0) || (area < smallest[0].area)) {
                return [Object.assign(Object.assign({}, current), { area })];
            }
            else if (area === smallest[0].area) {
                return [...smallest, Object.assign(Object.assign({}, current), { area })];
            }
            return smallest;
        }, [])
            // Reduce to position closest to center
            .reduce((closest, current) => {
            const [cx, cy] = polygons_1.centroid_polygon(current.poly);
            const distance = Math.sqrt(Math.pow(x - cx, 2) + Math.pow(y - cy, 2));
            if ((closest === null) || (distance < closest.distance)) {
                return Object.assign(Object.assign({}, current), { distance });
            }
            return closest;
        }, null));
        if (candidate === null)
            return null;
        return candidate.idx;
    }
}
exports.ImageCanvasView = ImageCanvasView;
//# sourceMappingURL=imagecanvas.js.map

/***/ }),

/***/ "./lib/polygons.js":
/*!*************************!*\
  !*** ./lib/polygons.js ***!
  \*************************/
/***/ ((__unused_webpack_module, exports) => {


Object.defineProperty(exports, "__esModule", ({ value: true }));
exports.area_polygon = exports.inside_polygon = exports.centroid_polygon = void 0;
function centroid_polygon(polygon) {
    const centroid = [0, 0];
    const { coords } = polygon;
    for (const [x, y] of coords) {
        centroid[0] += x;
        centroid[1] += y;
    }
    centroid[0] /= coords.length;
    centroid[1] /= coords.length;
    return centroid;
}
exports.centroid_polygon = centroid_polygon;
;
function inside_polygon(point, polygon) {
    // ray-casting algorithm based on
    // https://wrf.ecse.rpi.edu/Research/Short_Notes/pnpoly.html/pnpoly.html
    const x = point[0], y = point[1];
    const { coords } = polygon;
    var inside = false;
    for (let i = 0, j = coords.length - 1; i < coords.length; j = i++) {
        const xi = coords[i][0], yi = coords[i][1];
        const xj = coords[j][0], yj = coords[j][1];
        const intersect = ((yi > y) != (yj > y)) && (x < (xj - xi) * (y - yi) / (yj - yi) + xi);
        if (intersect) {
            inside = !inside;
        }
    }
    return inside;
}
exports.inside_polygon = inside_polygon;
;
function area_polygon(polygon) {
    const { coords } = polygon;
    let area = 0;
    for (let i = 0, j = coords.length - 1; i < coords.length; i++) {
        area += (coords[j][0] + coords[i][0]) * Math.abs(coords[j][1] - coords[i][1]);
        j = i;
    }
    return Math.abs(area / 2);
}
exports.area_polygon = area_polygon;
;
//# sourceMappingURL=polygons.js.map

/***/ }),

/***/ "./lib/serializers.js":
/*!****************************!*\
  !*** ./lib/serializers.js ***!
  \****************************/
/***/ ((__unused_webpack_module, exports) => {


Object.defineProperty(exports, "__esModule", ({ value: true }));
exports.serialize_numpy = exports.deserialize_numpy = void 0;
function deserialize_numpy(data) {
    if (data == null)
        return null;
    return {
        data: new Uint8ClampedArray(data.data.buffer),
        shape: data.shape,
    };
}
exports.deserialize_numpy = deserialize_numpy;
function serialize_numpy(data) {
    return data;
}
exports.serialize_numpy = serialize_numpy;
//# sourceMappingURL=serializers.js.map

/***/ }),

/***/ "./lib/version.js":
/*!************************!*\
  !*** ./lib/version.js ***!
  \************************/
/***/ ((__unused_webpack_module, exports, __webpack_require__) => {


// Copyright (c) 0phoff
// Distributed under the terms of the Modified BSD License.
Object.defineProperty(exports, "__esModule", ({ value: true }));
exports.MODULE_NAME = exports.MODULE_VERSION = void 0;
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
// eslint-disable-next-line @typescript-eslint/no-var-requires
const data = __webpack_require__(/*! ../package.json */ "./package.json");
/**
 * The _model_module_version/_view_module_version this package implements.
 *
 * The html widget manager assumes that this is the same as the npm package
 * version number.
 */
exports.MODULE_VERSION = data.version;
/*
 * The current package name.
 */
exports.MODULE_NAME = data.name;
//# sourceMappingURL=version.js.map

/***/ }),

/***/ "./package.json":
/*!**********************!*\
  !*** ./package.json ***!
  \**********************/
/***/ ((module) => {

module.exports = JSON.parse('{"name":"ibb","version":"2.1.0","description":"Jupyter Widget Library for Brambox","keywords":["jupyter","jupyterlab","jupyterlab-extension","widgets"],"files":["lib/**/*.js","dist/*.js","css/*.css"],"homepage":"https://github.com/0phoff/ibb","bugs":{"url":"https://github.com/0phoff/ibb/issues"},"license":"BSD-3-Clause","author":{"name":"0phoff","email":""},"main":"lib/index.js","types":"./lib/index.d.ts","repository":{"type":"git","url":"https://github.com//ibb"},"scripts":{"build":"yarn run build:lib && yarn run build:nbextension && yarn run build:labextension:dev","build:prod":"yarn run build:lib && yarn run build:nbextension && yarn run build:labextension","build:labextension":"jupyter labextension build .","build:labextension:dev":"jupyter labextension build --development True .","build:lib":"tsc","build:nbextension":"webpack","clean":"yarn run clean:lib && yarn run clean:nbextension && yarn run clean:labextension","clean:lib":"rimraf lib","clean:labextension":"rimraf ibb/labextension","clean:nbextension":"rimraf ibb/nbextension/static/index.js","lint":"eslint . --ext .ts,.tsx --fix","lint:check":"eslint . --ext .ts,.tsx","prepack":"yarn run build:lib","watch":"npm-run-all -p watch:*","watch:lib":"tsc -w","watch:nbextension":"webpack --watch --mode=development","watch:labextension":"jupyter labextension watch ."},"dependencies":{"@jupyter-widgets/base":"^1.1.10 || ^2.0.0 || ^3.0.0 || ^4.0.0","@jupyter-widgets/controls":"^3.1.1"},"devDependencies":{"@babel/core":"^7.5.0","@babel/preset-env":"^7.5.0","@jupyterlab/builder":"^3.0.0","@phosphor/application":"^1.6.0","@phosphor/widgets":"^1.6.0","@types/webpack-env":"^1.13.6","@typescript-eslint/eslint-plugin":"^3.6.0","@typescript-eslint/parser":"^3.6.0","acorn":"^7.2.0","css-loader":"^3.2.0","eslint":"^7.4.0","eslint-config-prettier":"^6.11.0","eslint-plugin-prettier":"^3.1.4","fs-extra":"^7.0.0","identity-obj-proxy":"^3.0.0","mkdirp":"^0.5.1","npm-run-all":"^4.1.3","prettier":"^2.0.5","rimraf":"^2.6.2","source-map-loader":"^1.1.3","style-loader":"^1.0.0","ts-loader":"^8.0.0","typescript":"~4.1.3","webpack":"^5.61.0","webpack-cli":"^4.0.0"},"jupyterlab":{"extension":"lib/plugin","outputDir":"ibb/labextension/","sharedPackages":{"@jupyter-widgets/base":{"bundled":false,"singleton":true}}}}');

/***/ })

}]);
//# sourceMappingURL=lib_imagecanvas_js.02d0b28f2c7b071a1033.js.map