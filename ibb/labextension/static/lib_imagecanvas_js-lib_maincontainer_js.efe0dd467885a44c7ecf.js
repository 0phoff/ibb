(self["webpackChunkibb"] = self["webpackChunkibb"] || []).push([["lib_imagecanvas_js-lib_maincontainer_js"],{

/***/ "./lib/imagecanvas.js":
/*!****************************!*\
  !*** ./lib/imagecanvas.js ***!
  \****************************/
/***/ ((__unused_webpack_module, exports, __webpack_require__) => {

"use strict";

// Copyright (c) 0phoff
// Distributed under the terms of the Modified BSD License.
Object.defineProperty(exports, "__esModule", ({ value: true }));
exports.ImageCanvasView = exports.ImageCanvasModel = void 0;
const base_1 = __webpack_require__(/*! @jupyter-widgets/base */ "webpack/sharing/consume/default/@jupyter-widgets/base?6b17");
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

/***/ "./lib/maincontainer.js":
/*!******************************!*\
  !*** ./lib/maincontainer.js ***!
  \******************************/
/***/ ((__unused_webpack_module, exports, __webpack_require__) => {

"use strict";

// Copyright (c) 0phoff
// Distributed under the terms of the Modified BSD License.
Object.defineProperty(exports, "__esModule", ({ value: true }));
exports.MainContainerView = exports.MainContainerModel = void 0;
const controls_1 = __webpack_require__(/*! @jupyter-widgets/controls */ "webpack/sharing/consume/default/@jupyter-widgets/controls/@jupyter-widgets/controls");
const version_1 = __webpack_require__(/*! ./version */ "./lib/version.js");
__webpack_require__(/*! ../css/maincontainer.css */ "./css/maincontainer.css");
class MainContainerModel extends controls_1.VBoxModel {
    defaults() {
        return Object.assign(Object.assign({}, super.defaults()), { _model_name: MainContainerModel.model_name, _model_module: MainContainerModel.model_module, _model_module_version: MainContainerModel.model_module_version, _view_name: MainContainerModel.view_name, _view_module: MainContainerModel.view_module, _view_module_version: MainContainerModel.view_module_version });
    }
}
exports.MainContainerModel = MainContainerModel;
MainContainerModel.model_name = 'MainContainerModel';
MainContainerModel.model_module = version_1.MODULE_NAME;
MainContainerModel.model_module_version = version_1.MODULE_VERSION;
MainContainerModel.view_name = 'MainContainerView';
MainContainerModel.view_module = version_1.MODULE_NAME;
MainContainerModel.view_module_version = version_1.MODULE_VERSION;
class MainContainerView extends controls_1.VBoxView {
    initialize(parameters) {
        super.initialize(parameters);
        this.pWidget.addClass('hide-unlink-children');
    }
}
exports.MainContainerView = MainContainerView;
//# sourceMappingURL=maincontainer.js.map

/***/ }),

/***/ "./lib/polygons.js":
/*!*************************!*\
  !*** ./lib/polygons.js ***!
  \*************************/
/***/ ((__unused_webpack_module, exports) => {

"use strict";

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

"use strict";

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

"use strict";

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

/***/ "./node_modules/css-loader/dist/cjs.js!./css/maincontainer.css":
/*!*********************************************************************!*\
  !*** ./node_modules/css-loader/dist/cjs.js!./css/maincontainer.css ***!
  \*********************************************************************/
/***/ ((module, exports, __webpack_require__) => {

// Imports
var ___CSS_LOADER_API_IMPORT___ = __webpack_require__(/*! ../node_modules/css-loader/dist/runtime/api.js */ "./node_modules/css-loader/dist/runtime/api.js");
exports = ___CSS_LOADER_API_IMPORT___(false);
// Module
exports.push([module.id, ".hide-unlink-children .jupyter-widgets-disconnected::before {\n    content: none !important;\n}\n", ""]);
// Exports
module.exports = exports;


/***/ }),

/***/ "./node_modules/css-loader/dist/runtime/api.js":
/*!*****************************************************!*\
  !*** ./node_modules/css-loader/dist/runtime/api.js ***!
  \*****************************************************/
/***/ ((module) => {

"use strict";


/*
  MIT License http://www.opensource.org/licenses/mit-license.php
  Author Tobias Koppers @sokra
*/
// css base code, injected by the css-loader
// eslint-disable-next-line func-names
module.exports = function (useSourceMap) {
  var list = []; // return the list of modules as css string

  list.toString = function toString() {
    return this.map(function (item) {
      var content = cssWithMappingToString(item, useSourceMap);

      if (item[2]) {
        return "@media ".concat(item[2], " {").concat(content, "}");
      }

      return content;
    }).join('');
  }; // import a list of modules into the list
  // eslint-disable-next-line func-names


  list.i = function (modules, mediaQuery, dedupe) {
    if (typeof modules === 'string') {
      // eslint-disable-next-line no-param-reassign
      modules = [[null, modules, '']];
    }

    var alreadyImportedModules = {};

    if (dedupe) {
      for (var i = 0; i < this.length; i++) {
        // eslint-disable-next-line prefer-destructuring
        var id = this[i][0];

        if (id != null) {
          alreadyImportedModules[id] = true;
        }
      }
    }

    for (var _i = 0; _i < modules.length; _i++) {
      var item = [].concat(modules[_i]);

      if (dedupe && alreadyImportedModules[item[0]]) {
        // eslint-disable-next-line no-continue
        continue;
      }

      if (mediaQuery) {
        if (!item[2]) {
          item[2] = mediaQuery;
        } else {
          item[2] = "".concat(mediaQuery, " and ").concat(item[2]);
        }
      }

      list.push(item);
    }
  };

  return list;
};

function cssWithMappingToString(item, useSourceMap) {
  var content = item[1] || ''; // eslint-disable-next-line prefer-destructuring

  var cssMapping = item[3];

  if (!cssMapping) {
    return content;
  }

  if (useSourceMap && typeof btoa === 'function') {
    var sourceMapping = toComment(cssMapping);
    var sourceURLs = cssMapping.sources.map(function (source) {
      return "/*# sourceURL=".concat(cssMapping.sourceRoot || '').concat(source, " */");
    });
    return [content].concat(sourceURLs).concat([sourceMapping]).join('\n');
  }

  return [content].join('\n');
} // Adapted from convert-source-map (MIT)


function toComment(sourceMap) {
  // eslint-disable-next-line no-undef
  var base64 = btoa(unescape(encodeURIComponent(JSON.stringify(sourceMap))));
  var data = "sourceMappingURL=data:application/json;charset=utf-8;base64,".concat(base64);
  return "/*# ".concat(data, " */");
}

/***/ }),

/***/ "./css/maincontainer.css":
/*!*******************************!*\
  !*** ./css/maincontainer.css ***!
  \*******************************/
/***/ ((module, __unused_webpack_exports, __webpack_require__) => {

var api = __webpack_require__(/*! !../node_modules/style-loader/dist/runtime/injectStylesIntoStyleTag.js */ "./node_modules/style-loader/dist/runtime/injectStylesIntoStyleTag.js");
            var content = __webpack_require__(/*! !!../node_modules/css-loader/dist/cjs.js!./maincontainer.css */ "./node_modules/css-loader/dist/cjs.js!./css/maincontainer.css");

            content = content.__esModule ? content.default : content;

            if (typeof content === 'string') {
              content = [[module.id, content, '']];
            }

var options = {};

options.insert = "head";
options.singleton = false;

var update = api(content, options);



module.exports = content.locals || {};

/***/ }),

/***/ "./node_modules/style-loader/dist/runtime/injectStylesIntoStyleTag.js":
/*!****************************************************************************!*\
  !*** ./node_modules/style-loader/dist/runtime/injectStylesIntoStyleTag.js ***!
  \****************************************************************************/
/***/ ((module, __unused_webpack_exports, __webpack_require__) => {

"use strict";


var isOldIE = function isOldIE() {
  var memo;
  return function memorize() {
    if (typeof memo === 'undefined') {
      // Test for IE <= 9 as proposed by Browserhacks
      // @see http://browserhacks.com/#hack-e71d8692f65334173fee715c222cb805
      // Tests for existence of standard globals is to allow style-loader
      // to operate correctly into non-standard environments
      // @see https://github.com/webpack-contrib/style-loader/issues/177
      memo = Boolean(window && document && document.all && !window.atob);
    }

    return memo;
  };
}();

var getTarget = function getTarget() {
  var memo = {};
  return function memorize(target) {
    if (typeof memo[target] === 'undefined') {
      var styleTarget = document.querySelector(target); // Special case to return head of iframe instead of iframe itself

      if (window.HTMLIFrameElement && styleTarget instanceof window.HTMLIFrameElement) {
        try {
          // This will throw an exception if access to iframe is blocked
          // due to cross-origin restrictions
          styleTarget = styleTarget.contentDocument.head;
        } catch (e) {
          // istanbul ignore next
          styleTarget = null;
        }
      }

      memo[target] = styleTarget;
    }

    return memo[target];
  };
}();

var stylesInDom = [];

function getIndexByIdentifier(identifier) {
  var result = -1;

  for (var i = 0; i < stylesInDom.length; i++) {
    if (stylesInDom[i].identifier === identifier) {
      result = i;
      break;
    }
  }

  return result;
}

function modulesToDom(list, options) {
  var idCountMap = {};
  var identifiers = [];

  for (var i = 0; i < list.length; i++) {
    var item = list[i];
    var id = options.base ? item[0] + options.base : item[0];
    var count = idCountMap[id] || 0;
    var identifier = "".concat(id, " ").concat(count);
    idCountMap[id] = count + 1;
    var index = getIndexByIdentifier(identifier);
    var obj = {
      css: item[1],
      media: item[2],
      sourceMap: item[3]
    };

    if (index !== -1) {
      stylesInDom[index].references++;
      stylesInDom[index].updater(obj);
    } else {
      stylesInDom.push({
        identifier: identifier,
        updater: addStyle(obj, options),
        references: 1
      });
    }

    identifiers.push(identifier);
  }

  return identifiers;
}

function insertStyleElement(options) {
  var style = document.createElement('style');
  var attributes = options.attributes || {};

  if (typeof attributes.nonce === 'undefined') {
    var nonce =  true ? __webpack_require__.nc : 0;

    if (nonce) {
      attributes.nonce = nonce;
    }
  }

  Object.keys(attributes).forEach(function (key) {
    style.setAttribute(key, attributes[key]);
  });

  if (typeof options.insert === 'function') {
    options.insert(style);
  } else {
    var target = getTarget(options.insert || 'head');

    if (!target) {
      throw new Error("Couldn't find a style target. This probably means that the value for the 'insert' parameter is invalid.");
    }

    target.appendChild(style);
  }

  return style;
}

function removeStyleElement(style) {
  // istanbul ignore if
  if (style.parentNode === null) {
    return false;
  }

  style.parentNode.removeChild(style);
}
/* istanbul ignore next  */


var replaceText = function replaceText() {
  var textStore = [];
  return function replace(index, replacement) {
    textStore[index] = replacement;
    return textStore.filter(Boolean).join('\n');
  };
}();

function applyToSingletonTag(style, index, remove, obj) {
  var css = remove ? '' : obj.media ? "@media ".concat(obj.media, " {").concat(obj.css, "}") : obj.css; // For old IE

  /* istanbul ignore if  */

  if (style.styleSheet) {
    style.styleSheet.cssText = replaceText(index, css);
  } else {
    var cssNode = document.createTextNode(css);
    var childNodes = style.childNodes;

    if (childNodes[index]) {
      style.removeChild(childNodes[index]);
    }

    if (childNodes.length) {
      style.insertBefore(cssNode, childNodes[index]);
    } else {
      style.appendChild(cssNode);
    }
  }
}

function applyToTag(style, options, obj) {
  var css = obj.css;
  var media = obj.media;
  var sourceMap = obj.sourceMap;

  if (media) {
    style.setAttribute('media', media);
  } else {
    style.removeAttribute('media');
  }

  if (sourceMap && typeof btoa !== 'undefined') {
    css += "\n/*# sourceMappingURL=data:application/json;base64,".concat(btoa(unescape(encodeURIComponent(JSON.stringify(sourceMap)))), " */");
  } // For old IE

  /* istanbul ignore if  */


  if (style.styleSheet) {
    style.styleSheet.cssText = css;
  } else {
    while (style.firstChild) {
      style.removeChild(style.firstChild);
    }

    style.appendChild(document.createTextNode(css));
  }
}

var singleton = null;
var singletonCounter = 0;

function addStyle(obj, options) {
  var style;
  var update;
  var remove;

  if (options.singleton) {
    var styleIndex = singletonCounter++;
    style = singleton || (singleton = insertStyleElement(options));
    update = applyToSingletonTag.bind(null, style, styleIndex, false);
    remove = applyToSingletonTag.bind(null, style, styleIndex, true);
  } else {
    style = insertStyleElement(options);
    update = applyToTag.bind(null, style, options);

    remove = function remove() {
      removeStyleElement(style);
    };
  }

  update(obj);
  return function updateStyle(newObj) {
    if (newObj) {
      if (newObj.css === obj.css && newObj.media === obj.media && newObj.sourceMap === obj.sourceMap) {
        return;
      }

      update(obj = newObj);
    } else {
      remove();
    }
  };
}

module.exports = function (list, options) {
  options = options || {}; // Force single-tag solution on IE6-9, which has a hard limit on the # of <style>
  // tags it will allow on a page

  if (!options.singleton && typeof options.singleton !== 'boolean') {
    options.singleton = isOldIE();
  }

  list = list || [];
  var lastIdentifiers = modulesToDom(list, options);
  return function update(newList) {
    newList = newList || [];

    if (Object.prototype.toString.call(newList) !== '[object Array]') {
      return;
    }

    for (var i = 0; i < lastIdentifiers.length; i++) {
      var identifier = lastIdentifiers[i];
      var index = getIndexByIdentifier(identifier);
      stylesInDom[index].references--;
    }

    var newLastIdentifiers = modulesToDom(newList, options);

    for (var _i = 0; _i < lastIdentifiers.length; _i++) {
      var _identifier = lastIdentifiers[_i];

      var _index = getIndexByIdentifier(_identifier);

      if (stylesInDom[_index].references === 0) {
        stylesInDom[_index].updater();

        stylesInDom.splice(_index, 1);
      }
    }

    lastIdentifiers = newLastIdentifiers;
  };
};

/***/ }),

/***/ "./package.json":
/*!**********************!*\
  !*** ./package.json ***!
  \**********************/
/***/ ((module) => {

"use strict";
module.exports = JSON.parse('{"name":"ibb","version":"2.1.0","description":"Jupyter Widget Library for Brambox","keywords":["jupyter","jupyterlab","jupyterlab-extension","widgets"],"files":["lib/**/*.js","dist/*.js","css/*.css"],"homepage":"https://github.com/0phoff/ibb","bugs":{"url":"https://github.com/0phoff/ibb/issues"},"license":"BSD-3-Clause","author":{"name":"0phoff","email":""},"main":"lib/index.js","types":"./lib/index.d.ts","repository":{"type":"git","url":"https://github.com//ibb"},"scripts":{"build":"yarn run build:lib && yarn run build:nbextension && yarn run build:labextension:dev","build:prod":"yarn run build:lib && yarn run build:nbextension && yarn run build:labextension","build:labextension":"jupyter labextension build .","build:labextension:dev":"jupyter labextension build --development True .","build:lib":"tsc","build:nbextension":"webpack","clean":"yarn run clean:lib && yarn run clean:nbextension && yarn run clean:labextension","clean:lib":"rimraf lib","clean:labextension":"rimraf ibb/labextension","clean:nbextension":"rimraf ibb/nbextension/static/index.js","lint":"eslint . --ext .ts,.tsx --fix","lint:check":"eslint . --ext .ts,.tsx","prepack":"yarn run build:lib","watch":"npm-run-all -p watch:*","watch:lib":"tsc -w","watch:nbextension":"webpack --watch --mode=development","watch:labextension":"jupyter labextension watch ."},"dependencies":{"@jupyter-widgets/base":"^1.1.10 || ^2.0.0 || ^3.0.0 || ^4.0.0","@jupyter-widgets/controls":"^3.1.1"},"devDependencies":{"@babel/core":"^7.5.0","@babel/preset-env":"^7.5.0","@jupyterlab/builder":"^3.0.0","@phosphor/application":"^1.6.0","@phosphor/widgets":"^1.6.0","@types/webpack-env":"^1.13.6","@typescript-eslint/eslint-plugin":"^3.6.0","@typescript-eslint/parser":"^3.6.0","acorn":"^7.2.0","css-loader":"^3.2.0","eslint":"^7.4.0","eslint-config-prettier":"^6.11.0","eslint-plugin-prettier":"^3.1.4","fs-extra":"^7.0.0","identity-obj-proxy":"^3.0.0","mkdirp":"^0.5.1","npm-run-all":"^4.1.3","prettier":"^2.0.5","rimraf":"^2.6.2","source-map-loader":"^1.1.3","style-loader":"^1.0.0","ts-loader":"^8.0.0","typescript":"~4.1.3","webpack":"^5.61.0","webpack-cli":"^4.0.0"},"jupyterlab":{"extension":"lib/plugin","outputDir":"ibb/labextension/","sharedPackages":{"@jupyter-widgets/base":{"bundled":false,"singleton":true}}}}');

/***/ })

}]);
//# sourceMappingURL=lib_imagecanvas_js-lib_maincontainer_js.efe0dd467885a44c7ecf.js.map