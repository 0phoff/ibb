var plugin = require('./index');
var base = require('@jupyter-widgets/base');

module.exports = {
  id: 'ibb',
  requires: [base.IJupyterWidgetRegistry],
  activate: function(app, widgets) {
      widgets.registerWidget({
          name: 'ibb',
          version: plugin.version,
          exports: plugin
      });
  },
  autoStart: true
};

