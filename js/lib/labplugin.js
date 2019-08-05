var plugin = require('./index');
var base = require('@jupyter-widgets/base');

module.exports = {
  id: 'itop',
  requires: [base.IJupyterWidgetRegistry],
  activate: function(app, widgets) {
      widgets.registerWidget({
          name: 'itop',
          version: plugin.version,
          exports: plugin
      });
  },
  autoStart: true
};

