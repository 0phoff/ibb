var widgets = require('@jupyter-widgets/base');
var _ = require('lodash');


function deserialize_numpy(data, manager) {
    if(data == null)
        return null;
    
    return {
        data: new Uint8ClampedArray(data.data.buffer),
        shape: data.shape,
    };
}

function serialize_numpy(data, manager) {
    return data;
}


var ImageCanvasModel = widgets.DOMWidgetModel.extend(
    {    
        defaults: _.extend(widgets.DOMWidgetModel.prototype.defaults(), {
            _model_module : 'itop',
            _model_name : 'ImageCanvasModel',
            _model_module_version : '0.1.0',
            _view_module : 'itop',
            _view_name : 'ImageCanvasView',
            _view_module_version : '0.1.0',                
        })
    },
    {
        serializers: _.extend({
            image: { deserialize: deserialize_numpy, serialize: serialize_numpy },
        }, widgets.DOMWidgetModel.serializers)
    }
);


var ImageCanvasView = widgets.DOMWidgetView.extend({
        render: function() {
            // Constants
            this.WIDTH = this.model.get('width');
            this.HEIGHT = this.model.get('height');
            this.RECT = this.model.get('enable_rect');
            this.ENLARGE = this.model.get('enlarge');
            this.COLOR = this.model.get('color');
            this.ALPHA = this.model.get('alpha');
            this.SIZE = this.model.get('size');
            this.HOVER = this.model.get('hover_style');
            this.CLICK = this.model.get('click_style');
            
            // Create elements
            this.bg = document.createElement('canvas');
            this.bg.width = this.WIDTH;
            this.bg.height = this.HEIGHT;
            this.bg.style.border = '1px solid lightgray';
            if (this.RECT) {
                this.fg = document.createElement('canvas');
                this.fg.width = this.WIDTH;
                this.fg.height = this.HEIGHT;
                this.fg.style.position = 'absolute';
                this.fg.style.top = '0px';
                this.fg.style.left = '0px';
                this.fg.style.right = '0px';
                this.fg.style.marginLeft = 'auto';
                this.fg.style.marginRight = 'auto';
                this.fx = document.createElement('canvas');
                this.fx.width = this.WIDTH;
                this.fx.height = this.HEIGHT;
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
            div.style.minWidth = this.WIDTH + 'px';
            div.style.minHeight = this.HEIGHT + 'px';
            div.appendChild(this.bg);
            if (this.RECT) {
                div.appendChild(this.fg);
                div.appendChild(this.fx);
            }
            this.el.appendChild(div);
                            
            // PY -> JS
            this.model.on('change:image', this.draw_image, this);
            if (this.RECT) {
                this.model.on('change:rectangles', this.draw_rectangles, this);
                if (this.HOVER != null)
                    this.model.on('change:hovered', this.draw_fx, this);
                if (this.CLICK != null)
                    this.model.on('change:clicked', this.draw_fx, this);
            }
            
            // JS -> PY
            if (this.RECT) {
                this.fx.onclick = this.onclick.bind(this);
                this.fx.onmousemove = this.onhover.bind(this);
                this.fx.onmouseleave = e => {
                    this.model.set('hovered', null);
                    this.touch();
                };
            }
            
            // Start
            this.draw_image()
            if (this.RECT)
                this.draw_rectangles()
        },

        draw_image: function() {
            var img = this.model.get('image'),
                bgctx = this.bg.getContext('2d');
            
            bgctx.clearRect(0, 0, this.bg.width, this.bg.height);
            this.scale = 1;
            this.offset_x = 0;
            this.offset_y = 0;
            
            if (img) {
                var imgd = new ImageData(img.data, img.shape[1], img.shape[0]);

                if (!this.ENLARGE && img.shape[1] <= this.WIDTH && img.shape[0] <= this.HEIGHT) {
                    this.offset_x = Math.floor((this.WIDTH - img.shape[1]) / 2);
                    this.offset_y = Math.floor((this.HEIGHT - img.shape[0]) / 2);
                    bgctx.putImageData(imgd, this.offset_x, this.offset_y);
                }
                else {
                    var oc = document.createElement('canvas'),
                        octx = oc.getContext('2d');
                    
                    // Compute scale and offset
                    this.scale = Math.min(this.WIDTH / img.shape[1], this.HEIGHT / img.shape[0]);
                    var scaled_w = img.shape[1] * this.scale,
                        scaled_h = img.shape[0] * this.scale;
                    
                    this.offset_x = Math.floor((this.WIDTH - scaled_w) / 2);
                    this.offset_y = Math.floor((this.HEIGHT - scaled_h) / 2);
                    
                    // Draw original image
                    oc.width = img.shape[1];
                    oc.height = img.shape[0];
                    octx.putImageData(imgd, 0, 0);
                    
                    // Draw rescaled image
                    bgctx.drawImage(oc, 0, 0, img.shape[1], img.shape[0], this.offset_x, this.offset_y, scaled_w, scaled_h);
                }
            }
        },
    
        draw_rectangles: function() {
            this.rect = this.model.get('rectangles');
            var fgctx = this.fg.getContext('2d');
            
            fgctx.clearRect(0, 0, this.fg.width, this.fg.height);
            if (this.rect)
                this.rect.forEach(rect => {this._draw_rect(fgctx, rect)});                
        },
    
        draw_fx: function() {
            var hover_idx = this.model.get('hovered'),
                click_idx = this.model.get('clicked'),
                fxctx = this.fx.getContext('2d');
            
            fxctx.clearRect(0, 0, this.fx.width, this.fx.height);
            if (this.rect) {
                if (hover_idx != null && hover_idx < this.rect.length) {
                    this._draw_rect(fxctx, this.rect[hover_idx], this.HOVER);
                }
                if (click_idx != null && click_idx < this.rect.length) {
                    this._draw_rect(fxctx, this.rect[click_idx], this.CLICK);
                }
            }
        },
    
        onclick: function(e) {
            var [x, y] = this._get_image_coord(e.clientX, e.clientY);
            this.model.set('clicked', this._get_closest_rect(x, y));
            this.touch();
        },
    
        onhover: function(e) {
            var [x, y] = this._get_image_coord(e.clientX, e.clientY);
            this.model.set('hovered', this._get_closest_rect(x, y));
            this.touch();
        },
    
        _draw_rect: function(ctx, rect, style=null) {
            var x = this.offset_x + (rect.x_top_left * this.scale),
                y = this.offset_y + (rect.y_top_left * this.scale),
                w = rect.width * this.scale,
                h = rect.height * this.scale;
            
            ctx.beginPath();
            ctx.rect(x, y, w, h);
            if (style) {
                ctx.strokeStyle = style.color || rect.color || this.COLOR;
                ctx.lineWidth = style.size || rect.size || this.SIZE;
                ctx.fillStyle = ctx.strokeStyle + (style.alpha || rect.alpha || this.ALPHA);
            }
            else {
                ctx.strokeStyle = rect.color || this.COLOR;
                ctx.lineWidth = rect.size || this.SIZE;
                ctx.fillStyle = ctx.strokeStyle + (rect.alpha || this.ALPHA);
            }

            ctx.stroke();
            ctx.fill();
        },
    
        _get_image_coord: function(x, y) {
            var r = this.fx.getBoundingClientRect();
                            
            x -= r.left + this.offset_x;
            y -= r.top + this.offset_y;
                            
            x /= this.scale;
            y /= this.scale;
                            
            return [x, y]
        },
    
        _get_closest_rect: function(x, y) {
            if (this.rect == null)
                return null;
            
            var candidate = this.rect
                // Remember original index
                .map((rect, idx) => {return {idx, rect}})
                // Filter boxes based on mouse position
                .filter(({rect}) => {
                    return (x >= rect.x_top_left) && (x <= rect.x_top_left + rect.width)
                        && (y >= rect.y_top_left) && (y <= rect.y_top_left + rect.height);
                })
                // Reduce to find smallest box
                .reduce((total, current, idx, arr) => {
                    if (!total.length)
                        total = arr;
                    
                    for (var i=0; i < total.length; i++) {
                        if (current.idx != total[i].idx
                            && current.rect.width <= total[i].rect.width
                            && current.rect.height <= total[i].rect.height)
                            total.splice(i, 1);
                    }
                    
                    return total;
                }, [])
                // Reduce to position closest to center
                .reduce((total, current) => {
                    var dx = Math.abs(x - (current.rect.x_top_left + current.rect.width / 2)),
                        dy = Math.abs(y - (current.rect.y_top_left + current.rect.height / 2)),
                        d = Math.sqrt(dx * dx + dy * dy);

                    if (total == null || d < total.d) {
                        return {
                            'idx': current.idx,
                            'rect': current.rect,
                            d
                        };
                    }
                    return total;
                }, null);
            
            if (candidate == null)
                return null;
            return candidate.idx;
        },
});


module.exports = {
    ImageCanvasModel: ImageCanvasModel,
    ImageCanvasView: ImageCanvasView,
}
