"use strict";
(self["webpackChunkibb"] = self["webpackChunkibb"] || []).push([["lib_plugin_js"],{

/***/ "./lib/plugin.js":
/*!***********************!*\
  !*** ./lib/plugin.js ***!
  \***********************/
/***/ (function(__unused_webpack_module, exports, __webpack_require__) {


// Copyright (c) 0phoff
// Distributed under the terms of the Modified BSD License.
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    Object.defineProperty(o, k2, { enumerable: true, get: function() { return m[k]; } });
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
Object.defineProperty(exports, "__esModule", ({ value: true }));
const base_1 = __webpack_require__(/*! @jupyter-widgets/base */ "webpack/sharing/consume/default/@jupyter-widgets/base?6b17");
const version_1 = __webpack_require__(/*! ./version */ "./lib/version.js");
const imageCanvasExports = __importStar(__webpack_require__(/*! ./imagecanvas */ "./lib/imagecanvas.js"));
const mainContainerExports = __importStar(__webpack_require__(/*! ./maincontainer */ "./lib/maincontainer.js"));
const EXTENSION_ID = 'ibb:plugin';
const ibbPlugin = {
    id: EXTENSION_ID,
    requires: [base_1.IJupyterWidgetRegistry],
    activate: activateWidgetExtension,
    autoStart: true,
};
// the "as unknown as ..." typecast above is solely to support JupyterLab 1
// and 2 in the same codebase and should be removed when we migrate to Lumino.
exports["default"] = ibbPlugin;
/**
 * Activate the widget extension.
 */
function activateWidgetExtension(app, registry) {
    registry.registerWidget({
        name: version_1.MODULE_NAME,
        version: version_1.MODULE_VERSION,
        exports: Object.assign(Object.assign({}, imageCanvasExports), mainContainerExports)
    });
}
//# sourceMappingURL=plugin.js.map

/***/ })

}]);
//# sourceMappingURL=lib_plugin_js.fd8bfdc5a4215d5ca282.js.map