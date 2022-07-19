// Copyright (c) 0phoff
// Distributed under the terms of the Modified BSD License.

import { VBoxModel, VBoxView } from '@jupyter-widgets/controls';
import { MODULE_NAME, MODULE_VERSION } from './version';
import '../css/maincontainer.css';

export class MainContainerModel extends VBoxModel {
  static model_name = 'MainContainerModel';
  static model_module = MODULE_NAME;
  static model_module_version = MODULE_VERSION;
  static view_name = 'MainContainerView';
  static view_module = MODULE_NAME;
  static view_module_version = MODULE_VERSION;

  defaults() {
    return {
      ...super.defaults(),
      _model_name: MainContainerModel.model_name,
      _model_module: MainContainerModel.model_module,
      _model_module_version: MainContainerModel.model_module_version,
      _view_name: MainContainerModel.view_name,
      _view_module: MainContainerModel.view_module,
      _view_module_version: MainContainerModel.view_module_version,
    };
  }
}

export class MainContainerView extends VBoxView {
  initialize(parameters: any): void {
    super.initialize(parameters);
    this.pWidget.addClass('hide-unlink-children');
  }
}
