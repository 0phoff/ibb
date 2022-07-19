"use strict";
// Copyright (c) 0phoff
// Distributed under the terms of the Modified BSD License.
Object.defineProperty(exports, "__esModule", { value: true });
exports.ExampleView = exports.ExampleModel = void 0;
const base_1 = require("@jupyter-widgets/base");
const version_1 = require("./version");
// Import the CSS
require("../css/widget.css");
class ExampleModel extends base_1.DOMWidgetModel {
    defaults() {
        return Object.assign(Object.assign({}, super.defaults()), { _model_name: ExampleModel.model_name, _model_module: ExampleModel.model_module, _model_module_version: ExampleModel.model_module_version, _view_name: ExampleModel.view_name, _view_module: ExampleModel.view_module, _view_module_version: ExampleModel.view_module_version, value: 'Hello World' });
    }
}
exports.ExampleModel = ExampleModel;
ExampleModel.serializers = Object.assign({}, base_1.DOMWidgetModel.serializers);
ExampleModel.model_name = 'ExampleModel';
ExampleModel.model_module = version_1.MODULE_NAME;
ExampleModel.model_module_version = version_1.MODULE_VERSION;
ExampleModel.view_name = 'ExampleView'; // Set to null if no view
ExampleModel.view_module = version_1.MODULE_NAME; // Set to null if no view
ExampleModel.view_module_version = version_1.MODULE_VERSION;
class ExampleView extends base_1.DOMWidgetView {
    render() {
        this.el.classList.add('custom-widget');
        this.value_changed();
        this.model.on('change:value', this.value_changed, this);
    }
    value_changed() {
        this.el.textContent = this.model.get('value');
    }
}
exports.ExampleView = ExampleView;
//# sourceMappingURL=widget.js.map