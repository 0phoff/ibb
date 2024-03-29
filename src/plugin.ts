// Copyright (c) 0phoff
// Distributed under the terms of the Modified BSD License.

import { Application, IPlugin } from '@lumino/application';
import { Widget } from '@lumino/widgets';
import { ExportData, IJupyterWidgetRegistry } from '@jupyter-widgets/base';
import { MODULE_NAME, MODULE_VERSION } from './version';

import '../css/ibb.css';
import * as imageCanvasExports from './imagecanvas';
import * as unlinkBoxExports from './unlinkbox';
import * as repeatButtonExports from './repeatbutton';

const EXTENSION_ID = 'ibb:plugin';

const ibbPlugin: IPlugin<Application<Widget>, void> = {
  id: EXTENSION_ID,
  requires: [IJupyterWidgetRegistry],
  activate: activateWidgetExtension,
  autoStart: true,
} as IPlugin<Application<Widget>, void>;

export default ibbPlugin;

/**
 * Activate the widget extension.
 */
function activateWidgetExtension(app: Application<Widget>, registry: IJupyterWidgetRegistry): void {
  registry.registerWidget({
    name: MODULE_NAME,
    version: MODULE_VERSION,
    exports: {
      ...imageCanvasExports,
      ...(unlinkBoxExports as ExportData),
      ...repeatButtonExports,
    },
  });
}
