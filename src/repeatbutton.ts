// Copyright (c) 0phoff
// Distributed under the terms of the Modified BSD License.

import { ButtonModel, ButtonView } from '@jupyter-widgets/controls';
import { MODULE_NAME, MODULE_VERSION } from './version';

export class RepeatButtonModel extends ButtonModel {
  static model_name = 'RepeatButtonModel';
  static model_module = MODULE_NAME;
  static model_module_version = MODULE_VERSION;
  static view_name = 'RepeatButtonView';
  static view_module = MODULE_NAME;
  static view_module_version = MODULE_VERSION;

  defaults() {
    return {
      ...super.defaults(),
      _model_name: RepeatButtonModel.model_name,
      _model_module: RepeatButtonModel.model_module,
      _model_module_version: RepeatButtonModel.model_module_version,
      _view_name: RepeatButtonModel.view_name,
      _view_module: RepeatButtonModel.view_module,
      _view_module_version: RepeatButtonModel.view_module_version,
    };
  }
}

export class RepeatButtonView extends ButtonView {
  private timeoutRef?: number;
  private intervalRef?: number;

  events(): { [e: string]: string } {
    return {
      mousedown: '_handle_down',
      mouseup: '_handle_up',
      mouseleave: '_handle_up',

      touchstart: '_handle_down',
      touchend: '_handle_up',
    };
  }

  _handle_down(evt: MouseEvent) {
    // Fire once (aka click)
    this._handle_click(evt);

    // Setup repeat
    const timeoutTime = Math.trunc(this.model.get('delay') * 1000);
    this.timeoutRef = window.setTimeout(() => {
      // First repeat instance after delay
      this.send({ event: 'click' });

      // Set interval for next repeats
      const intervalTime = Math.trunc(1000 / this.model.get('frequency'));
      this.intervalRef = window.setInterval(() => {
        this.send({ event: 'click' });
      }, intervalTime);
      this.timeoutRef = undefined;
    }, timeoutTime);
  }

  _handle_up(evt: MouseEvent) {
    evt.preventDefault();

    if (this.timeoutRef) {
      window.clearTimeout(this.timeoutRef);
      this.timeoutRef = undefined;
    }
    if (this.intervalRef) {
      window.clearInterval(this.intervalRef);
      this.intervalRef = undefined;
    }
  }
}
