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

function centroid_polygon(poly) {
    const centroid = [0, 0];
    for (const [x, y] of poly) {
        centroid[0] += x;
        centroid[1] += y;
    }

    centroid[0] /= poly.length;
    centroid[1] /= poly.length;

    return centroid;
};

function inside_polygon(point, poly) {
    // ray-casting algorithm based on
    // https://wrf.ecse.rpi.edu/Research/Short_Notes/pnpoly.html/pnpoly.html
    
    var x = point[0], y = point[1];
    
    var inside = false;
    for (var i = 0, j = poly.length - 1; i < poly.length; j = i++) {
        var xi = poly[i][0], yi = poly[i][1];
        var xj = poly[j][0], yj = poly[j][1];
        
        var intersect = ((yi > y) != (yj > y))
            && (x < (xj - xi) * (y - yi) / (yj - yi) + xi);
        if (intersect) inside = !inside;
    }
    
    return inside;
};

function area_polygon(poly) {
    area = 0;

    for (let i=0, j=poly.length - 1; i < poly.length; i++) {
        area += (poly[j][0] + poly[i][0]) * Math.abs(poly[j][1] - poly[i][1]); 
        j = i;
    }   

    return Math.abs(area / 2);
};


var ImageCanvasModel = widgets.DOMWidgetModel.extend(
    {    
        defaults: _.extend(widgets.DOMWidgetModel.prototype.defaults(), {
            _model_module : 'ibb',
            _model_name : 'ImageCanvasModel',
            _model_module_version : '2.0.0',
            _view_module : 'ibb',
            _view_name : 'ImageCanvasView',
            _view_module_version : '2.0.0',                
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
            this.POLY = this.model.get('enable_poly');
            this.ENLARGE = this.model.get('enlarge');
            this.COLOR = this.model.get('color');
            this.ALPHA = this.model.get('alpha');
            this.SIZE = this.model.get('size');
            this.HOVER = this.model.get('hover_style');
            this.CLICK = this.model.get('click_style');
                            
            // PY -> JS
            this.model.on('change:width', this.render_children, this);
            this.model.on('change:height', this.render_children, this);
            this.model.on('change:image', this.draw_image, this);
            this.model.on('change:save', this.save, this);
            if (this.POLY) {
                this.model.on('change:polygons', this.draw_polygons, this);
                if (this.HOVER != null)
                    this.model.on('change:hovered', this.draw_fx, this);
                if (this.CLICK != null)
                    this.model.on('change:clicked', this.draw_fx, this);
            }
            
            // Start
            this.render_children()
        },

        render_children: function() {
            // Constants
            this.width = this.model.get('width') - 2;
            this.height = this.model.get('height') - 2;
            
            // Create elements
            this.bg = document.createElement('canvas');
            this.bg.width = this.width;
            this.bg.height = this.height;
            this.bg.style.border = '1px solid lightgray';
            this.result = document.createElement('canvas');
            this.result.width = this.width;
            this.result.height = this.height;
            if (this.POLY) {
                this.fg = document.createElement('canvas');
                this.fg.width = this.width;
                this.fg.height = this.height;
                this.fg.style.position = 'absolute';
                this.fg.style.top = '0px';
                this.fg.style.left = '0px';
                this.fg.style.right = '0px';
                this.fg.style.marginLeft = 'auto';
                this.fg.style.marginRight = 'auto';
                this.fx = document.createElement('canvas');
                this.fx.width = this.width;
                this.fx.height = this.height;
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
            div.style.minWidth = this.width + 'px';
            div.style.minHeight = this.height + 'px';
            div.appendChild(this.bg);
            if (this.POLY) {
                div.appendChild(this.fg);
                div.appendChild(this.fx);
            }

            while (this.el.firstChild) this.el.firstChild.remove();
            this.el.appendChild(div);

            this.draw_image()
            if (this.POLY) {
                this.draw_polygons()
                this.draw_fx()
                this.fx.onclick = this.onclick.bind(this);
                this.fx.onmousemove = this.onhover.bind(this);
                this.fx.onmouseleave = e => {
                    this.model.set('hovered', null);
                    this.touch();
                };
            }
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

                if (!this.ENLARGE && img.shape[1] <= this.width && img.shape[0] <= this.height) {
                    this.offset_x = Math.floor((this.width - img.shape[1]) / 2);
                    this.offset_y = Math.floor((this.height - img.shape[0]) / 2);
                    bgctx.putImageData(imgd, this.offset_x, this.offset_y);
                }
                else {
                    var oc = document.createElement('canvas'),
                        octx = oc.getContext('2d');
                    
                    // Compute scale and offset
                    this.scale = Math.min(this.width / img.shape[1], this.height / img.shape[0]);
                    var scaled_w = img.shape[1] * this.scale,
                        scaled_h = img.shape[0] * this.scale;
                    
                    this.offset_x = Math.floor((this.width - scaled_w) / 2);
                    this.offset_y = Math.floor((this.height - scaled_h) / 2);
                    
                    // Draw original image
                    oc.width = img.shape[1];
                    oc.height = img.shape[0];
                    octx.putImageData(imgd, 0, 0);
                    
                    // Draw rescaled image
                    bgctx.drawImage(oc, 0, 0, img.shape[1], img.shape[0], this.offset_x, this.offset_y, scaled_w, scaled_h);
                }
            }
        },

        draw_polygons: function() {
            this.poly = this.model.get('polygons');
            var fgctx = this.fg.getContext('2d');
            
            fgctx.clearRect(0, 0, this.fg.width, this.fg.height);
            if (this.poly)
                this.poly.forEach(poly => {this._draw_poly(fgctx, poly)});                
        },
    
        draw_fx: function() {
            var hover_idx = this.model.get('hovered'),
                click_idx = this.model.get('clicked'),
                fxctx = this.fx.getContext('2d');
            
            fxctx.clearRect(0, 0, this.fx.width, this.fx.height);
            if (this.poly) {
                if (hover_idx != null && hover_idx < this.poly.length) {
                    this._draw_poly(fxctx, this.poly[hover_idx], this.HOVER);
                }
                if (click_idx != null && click_idx < this.poly.length) {
                    this._draw_poly(fxctx, this.poly[click_idx], this.CLICK);
                }
            }
        },

        save: function() {
            var save_val = this.model.get('save');

            if (save_val) {
                // Clear result canvas
                var ctx = this.result.getContext('2d');
                ctx.clearRect(0, 0, this.width, this.height);

                // Draw canvases
                ctx.drawImage(this.bg, 0, 0, this.width, this.height);
                if (this.POLY) {
                    ctx.drawImage(this.fg, 0, 0, this.width, this.height);
                    ctx.drawImage(this.fx, 0, 0, this.width, this.height);
                }

                // Open in new tab
                var data = this.result.toDataURL('png');
                var w = window.open('about:blank');
                setTimeout(function() {
                  w.document.body.appendChild(w.document.createElement('img')).src = data;
                }, 0);

                // Reset save
                setTimeout(() => {
                  this.model.set('save', false);
                  this.model.save_changes();
                }, 0);
            }
        },
    
        onclick: function(e) {
            var [x, y] = this._get_image_coord(e.clientX, e.clientY);
            this.model.set('clicked', this._get_closest_poly(x, y));
            this.touch();
        },
    
        onhover: function(e) {
            var [x, y] = this._get_image_coord(e.clientX, e.clientY);
            this.model.set('hovered', this._get_closest_poly(x, y));
            this.touch();
        },
    
        _draw_poly: function(ctx, poly, style=null) {
            const coords = poly.coords.map(([x, y]) => [
              this.offset_x + (x * this.scale),
              this.offset_y + (y * this.scale)
            ]);

            // Draw
            ctx.beginPath();
            ctx.moveTo(coords[0][0], coords[0][1]);
            for (const [x, y] of coords.slice(1)) {
                ctx.lineTo(x, y);
            }
            ctx.closePath();
            
            // Styles
            if (style) {
                ctx.strokeStyle = style.color || poly.color || this.COLOR;
                ctx.lineWidth = style.size || poly.size || this.SIZE;
                ctx.fillStyle = ctx.strokeStyle + (style.alpha || poly.alpha || this.ALPHA);
            }
            else {
                ctx.strokeStyle = poly.color || this.COLOR;
                ctx.lineWidth = poly.size || this.SIZE;
                ctx.fillStyle = ctx.strokeStyle + (poly.alpha || this.ALPHA);
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
    
        _get_closest_poly: function(x, y) {
            if (this.poly === null || this.poly.length === 0)
                return null;

            var candidate = (this.poly
                // Remember original index
                .map((poly, idx) => {return {idx, poly}})
                // Filter boxes based on mouse position
                .filter(({poly}) => inside_polygon([x, y], poly.coords))
                // Reduce to find smallest box
                .reduce((smallest, current) => {
                    const area = area_polygon(current.poly.coords);

                    if ((smallest.length === 0) || (area < smallest[0].area)) {
                        return [{...current, area}];
                    } else if (area === smallest[0].area) {
                        return [...smallest, {...current, area}];
                    }
                    return smallest;
                }, [])
                // Reduce to position closest to center
                .reduce((closest, current) => {
                    const [cx, cy] = centroid_polygon(current.poly.coords);
                    const distance = Math.sqrt(Math.pow(x - cx, 2) + Math.pow(y - cy, 2));

                    if ((closest === null) || (distance < closest.distance)) {
                        return {...current, distance};
                    }
                    return closest;
                }, null)
            );

            if (candidate === null)
                return null;
            return candidate.idx;
        },
});


module.exports = {
    ImageCanvasModel: ImageCanvasModel,
    ImageCanvasView: ImageCanvasView,
}
