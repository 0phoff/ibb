"use strict";
// Copyright (c) 0phoff
// Distributed under the terms of the Modified BSD License.
Object.defineProperty(exports, "__esModule", { value: true });
exports.MainContainerView = exports.MainContainerModel = void 0;
const controls_1 = require("@jupyter-widgets/controls");
const version_1 = require("./version");
require("../css/maincontainer.css");
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