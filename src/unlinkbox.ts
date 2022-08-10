// Copyright (c) 0phoff
// Distributed under the terms of the Modified BSD License.

import { BoxModel, BoxView } from '@jupyter-widgets/controls';
import { MODULE_NAME, MODULE_VERSION } from './version';

export class UnlinkBoxModel extends BoxModel {
  static model_name = 'UnlinkBoxModel';
  static model_module = MODULE_NAME;
  static model_module_version = MODULE_VERSION;
  static view_name = 'UnlinkBoxView';
  static view_module = MODULE_NAME;
  static view_module_version = MODULE_VERSION;

  defaults() {
    return {
      ...super.defaults(),
      _model_name: UnlinkBoxModel.model_name,
      _model_module: UnlinkBoxModel.model_module,
      _model_module_version: UnlinkBoxModel.model_module_version,
      _view_name: UnlinkBoxModel.view_name,
      _view_module: UnlinkBoxModel.view_module,
      _view_module_version: UnlinkBoxModel.view_module_version,
    };
  }
}

export class UnlinkBoxView extends BoxView {
  initialize(parameters: any): void {
    super.initialize(parameters);

    const type = this.model.get('type');
    if (type === 'grid') {
      this.pWidget.addClass('widget-gridbox');
      this.pWidget.removeClass('widget-box');
    } else if (type === 'vbox') {
      this.pWidget.addClass('widget-vbox');
    } else {
      this.pWidget.addClass('widget-hbox');
    }

    this.pWidget.addClass('ibb-unlink');
  }
}
